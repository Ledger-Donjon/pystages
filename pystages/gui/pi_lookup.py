# This file is part of pystages
#
# pystages is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright 2018-2026 Ledger SAS, written by Michaël Mouchous

"""
Standalone tool to display and update the joystick lookup table of a PI
C-863.12 controller.

The lookup table is not part of the :class:`pystages.PI` API: the GCS commands
(``JLT``, ``JLT?``, ``JDT``) are sent from here.
"""

from __future__ import annotations

import atexit
import signal
import sys
from functools import partial

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QColor, QPainter, QPen, QPaintEvent
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from ..exceptions import ConnectionFailure, ProtocolError
from ..pi import PI

LOOKUP_TABLE_SIZE = 256
LINEAR = 1
PARABOLIC = 2
# Number of table points sent per JLT command.
WRITE_CHUNK = 16
SLIDER_SCALE = 100
# Physical button on address 1 divides every axis velocity by 4 while held.
# Physical button on address 2 divides every axis velocity by 2 while held.
# Physical button on address 3 toggles every axis joystick on each press.
BUTTON_VELOCITY_DIVISOR = {1: 4, 2: 2}
BUTTON_JOYSTICK_MASTER_ADDRESS = 3


def read_lookup_table(stage: PI, address: int) -> list[float]:
    """Read the 256 velocity factors of the joystick lookup table (``JLT?``)."""
    query = f"{address} JLT? 1 {LOOKUP_TABLE_SIZE}"
    try:
        stage.serial.write(f"{query}\n".encode("utf-8"))
    except Exception as exc:
        raise ConnectionFailure(
            f"Failed to write '{query}' to the controller."
        ) from exc
    values: list[float] = []
    in_header = True
    while len(values) < LOOKUP_TABLE_SIZE:
        try:
            line = stage.serial.readline().decode("utf-8").strip()
        except Exception as exc:
            raise ConnectionFailure(
                f"Failed to read response to '{query}' from the controller."
            ) from exc
        if not line:
            break
        if in_header:
            in_header = not line.upper().endswith("END_HEADER")
            continue
        try:
            values += [float(token) for token in line.split()]
        except ValueError:
            raise ProtocolError(query=query, response=line, expected="float values")
    if len(values) != LOOKUP_TABLE_SIZE:
        raise ProtocolError(
            query=query,
            response=f"{len(values)} values",
            expected=f"{LOOKUP_TABLE_SIZE} values",
        )
    return values


def write_lookup_table(stage: PI, address: int, values: list[float]) -> None:
    """
    Write the joystick lookup table (``JLT``).

    Values are stored in the controller non-volatile memory, which supports a
    limited number of write cycles.
    """
    if len(values) != LOOKUP_TABLE_SIZE:
        raise ValueError(f"Expected {LOOKUP_TABLE_SIZE} values, got {len(values)}")
    if any(value < -1.0 or value > 1.0 for value in values):
        raise ValueError("Lookup table values must be in [-1.0, 1.0]")
    for start in range(0, LOOKUP_TABLE_SIZE, WRITE_CHUNK):
        chunk = " ".join(f"{v:.4f}" for v in values[start : start + WRITE_CHUNK])
        stage.send(address, f"JLT 1 1 {start + 1} {chunk}")


def load_default_lookup_table(stage: PI, address: int, table_type: int) -> None:
    """Load a firmware lookup table profile: linear or parabolic (``JDT``)."""
    stage.send(address, f"JDT 1 1 {table_type}")


class LookupPlot(QWidget):
    """Polyline of the lookup table factors, from -1 to 1."""

    def __init__(self) -> None:
        super().__init__()
        self.values: list[float] = [0.0] * LOOKUP_TABLE_SIZE
        self.setMinimumHeight(160)

    def set_values(self, values: list[float]) -> None:
        self.values = values
        self.update()

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        if a0 is None:
            return
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        margin = 10
        width = max(1, self.width() - 2 * margin)
        height = max(1, self.height() - 2 * margin)
        painter.setPen(QPen(QColor(90, 90, 90)))
        painter.drawRect(margin, margin, width, height)
        painter.drawLine(
            margin, margin + height // 2, margin + width, margin + height // 2
        )

        painter.setPen(QPen(QColor(80, 160, 255), 2))
        points = [
            (
                margin + width * i / (len(self.values) - 1),
                margin + height * (1.0 - (max(-1.0, min(1.0, value)) + 1.0) / 2.0),
            )
            for i, value in enumerate(self.values)
        ]
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            painter.drawLine(int(x0), int(y0), int(x1), int(y1))


class MotionSlider(QWidget):
    """
    Slider for one closed-loop motion setting of an axis.

    ``released`` is emitted when the user drops the handle, ``restore_asked``
    when the restore button is clicked. ``initial`` is the value read at
    connection time, and ``restored`` tells whether it has been sent back.
    """

    released = pyqtSignal()
    restore_asked = pyqtSignal()

    def __init__(self, title: str) -> None:
        super().__init__()
        self.title = title
        self.initial: float | None = None
        self.maximum = 0.01
        self.restored = True

        box = QHBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(box)
        box.addWidget(QLabel(title))
        self.value_label = QLabel("—")
        self.value_label.setMinimumWidth(48)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(
            lambda: self.value_label.setText(f"{self.value():g}")
        )
        self.slider.sliderReleased.connect(self.released)
        box.addWidget(self.slider, stretch=1)
        box.addWidget(self.value_label)
        button = QPushButton("Restore initial")
        button.clicked.connect(self.restore_asked)
        box.addWidget(button)
        self.info_label = QLabel("")
        box.addWidget(self.info_label)

    def value(self) -> float:
        return self.slider.value() / SLIDER_SCALE

    def set_value(self, value: float) -> None:
        self.slider.setValue(round(min(self.maximum, max(0.0, value)) * SLIDER_SCALE))

    def configure(self, initial: float, maximum: float, info: str = "") -> None:
        """Set the slider range from the values read on the controller."""
        self.initial = initial
        self.maximum = max(maximum, initial, 0.01)
        self.slider.setRange(0, round(self.maximum * SLIDER_SCALE))
        self.set_value(initial)
        self.restored = False
        self.info_label.setText(
            f"(initial: {initial:g}, range: 0–{self.maximum:g}{info})"
        )

    def reset(self) -> None:
        self.initial = None
        self.slider.setRange(0, SLIDER_SCALE)
        self.slider.setValue(0)
        self.value_label.setText("—")
        self.info_label.setText("")


class PILookupTab(QWidget):
    """Controls for one controller address."""

    def __init__(self, address: int, address_index: int) -> None:
        super().__init__()
        self.address = address
        self.address_index = address_index
        self.stage: PI | None = None
        self.lookup_window: PILookupWindow | None = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Velocity is applied to every axis at once, to honour the divisor of
        # the physical buttons, hence its dedicated slots.
        self.velocity = MotionSlider("Velocity")
        self.velocity.released.connect(self.apply_velocity)
        self.velocity.restore_asked.connect(self.restore_initial_velocity)
        layout.addWidget(self.velocity)

        self.acceleration = MotionSlider("Acceleration")
        self.deceleration = MotionSlider("Deceleration")
        for slider, command in ((self.acceleration, "ACC"), (self.deceleration, "DEC")):
            layout.addWidget(slider)
            slider.released.connect(partial(self.apply_ramp, slider, command))
            slider.restore_asked.connect(partial(self.restore_ramp, slider, command))

        self.settings = (
            (self.velocity, "VEL"),
            (self.acceleration, "ACC"),
            (self.deceleration, "DEC"),
        )

        box = QHBoxLayout()
        layout.addLayout(box)
        self.joystick_button = QPushButton("Joystick disabled")
        self.joystick_button.setCheckable(True)
        self.joystick_button.clicked.connect(self.toggle_joystick)
        box.addWidget(self.joystick_button)
        box.addWidget(QLabel("Button"))
        self.joystick_button_indicator = QLabel()
        self.joystick_button_indicator.setFixedSize(16, 16)
        box.addWidget(self.joystick_button_indicator)
        self.invert_direction_checkbox = QCheckBox("Invert direction")
        self.invert_direction_checkbox.clicked.connect(self.toggle_invert_direction)
        box.addWidget(self.invert_direction_checkbox)
        box.addStretch()
        self.show_joystick(False)
        self.show_button(False, connected=False)

        self.plot = LookupPlot()
        layout.addWidget(self.plot)

        self.table = QTableWidget(LOOKUP_TABLE_SIZE, 1)
        self.table.setHorizontalHeaderLabels(["Factor"])
        self.table.setVerticalHeaderLabels(
            [str(i + 1) for i in range(LOOKUP_TABLE_SIZE)]
        )
        for row in range(LOOKUP_TABLE_SIZE):
            self.table.setItem(row, 0, QTableWidgetItem("0.0000"))
        self.table.itemChanged.connect(self.refresh_plot)
        layout.addWidget(self.table)

        box = QHBoxLayout()
        layout.addLayout(box)
        for label, slot in (
            ("Read", self.read_table),
            ("Linear", lambda: self.load_default(LINEAR)),
            ("Parabolic", lambda: self.load_default(PARABOLIC)),
            ("Write", self.write_table),
        ):
            button = QPushButton(label)
            button.clicked.connect(slot)
            box.addWidget(button)

        self.status = QLabel("Disconnected")
        layout.addWidget(self.status)

    def bind_stage(self, stage: PI) -> None:
        self.stage = stage
        index = self.address_index
        limits = stage.velocity_limits[index]
        self.velocity.configure(
            stage.velocity[index], limits.maximum, f", default: {limits.default:g}"
        )
        self.acceleration.configure(
            stage.acceleration[index], stage.acceleration_max[index]
        )
        self.deceleration.configure(
            stage.deceleration[index], stage.deceleration_max[index]
        )
        self.sync_joystick_state()
        self.sync_invert_direction()
        self.read_table()
        self.status.setText(f"Connected to controller {self.address}")

    def unbind_stage(self) -> None:
        self.restore_initial_settings()
        self.stage = None
        for slider, _ in self.settings:
            slider.reset()
        self.show_joystick(False)
        self.show_button(False, connected=False)
        self.invert_direction_checkbox.setChecked(False)
        self.lookup_window = None
        self.status.setText("Disconnected")

    def show_joystick(self, enabled: bool) -> None:
        self.joystick_button.setChecked(enabled)
        self.joystick_button.setText(
            "Joystick enabled" if enabled else "Joystick disabled"
        )

    def show_button(self, pressed: bool, *, connected: bool = True) -> None:
        if not connected:
            color = "#555555"
            status = "disconnected"
        elif pressed:
            color = "#ffc107"
            status = "pressed"
        else:
            color = "#333333"
            status = "released"

        self.joystick_button_indicator.setStyleSheet(
            f"QLabel {{ background-color: {color}; border-radius: 8px; "
            f"border: 1px solid #333; }}"
        )
        self.joystick_button_indicator.setToolTip(f"Joystick button: {status}")

    def sync_joystick_state(self) -> None:
        if self.stage is None:
            return
        try:
            self.show_joystick(self.stage.joystick_enabled[self.address_index])
        except ProtocolError as exc:
            QMessageBox.critical(
                self, f"Address {self.address}: joystick state read failed", str(exc)
            )

    def toggle_joystick(self, enabled: bool) -> None:
        """Enable or disable the joystick of this address only."""
        if self.stage is None:
            return
        try:
            states = self.stage.joystick_enabled
            states[self.address_index] = enabled
            self.stage.joystick_enabled = states
            self.status.setText("Joystick enabled" if enabled else "Joystick disabled")
            self.show_joystick(enabled)
        except ProtocolError as exc:
            self.show_joystick(not enabled)
            QMessageBox.critical(
                self, f"Address {self.address}: joystick toggle failed", str(exc)
            )

    def sync_invert_direction(self) -> None:
        if self.stage is None:
            return
        try:
            inverted = self.stage.joystick_direction_inverted[self.address_index]
            self.invert_direction_checkbox.blockSignals(True)
            self.invert_direction_checkbox.setChecked(inverted)
            self.invert_direction_checkbox.blockSignals(False)
        except ProtocolError as exc:
            QMessageBox.critical(
                self, f"Address {self.address}: invert direction read failed", str(exc)
            )

    def toggle_invert_direction(self, inverted: bool) -> None:
        if self.stage is None:
            return
        try:
            values = list(self.stage.joystick_direction_inverted)
            values[self.address_index] = inverted
            self.stage.joystick_direction_inverted = values
            self.status.setText(
                "Joystick direction inverted"
                if inverted
                else "Joystick direction normal"
            )
        except ProtocolError as exc:
            self.invert_direction_checkbox.blockSignals(True)
            self.invert_direction_checkbox.setChecked(not inverted)
            self.invert_direction_checkbox.blockSignals(False)
            QMessageBox.critical(
                self, f"Address {self.address}: invert direction failed", str(exc)
            )

    def apply_velocity(self) -> None:
        if self.lookup_window is None:
            return
        self.lookup_window.apply_all_velocities()
        value = self.velocity.value()
        divisor = self.lookup_window.velocity_divisor
        active = f" ({value / divisor:g} active on all axes)" if divisor > 1 else ""
        self.status.setText(f"Velocity set to {value:g}{active}")

    def restore_initial_velocity(self) -> None:
        if self.velocity.initial is None:
            return
        self.velocity.set_value(self.velocity.initial)
        self.apply_velocity()

    def apply_ramp(self, slider: MotionSlider, command: str) -> None:
        """Send the slider value as ``ACC`` or ``DEC`` for this address."""
        if self.stage is None:
            return
        self.stage.send(self.address, f"{command} 1 {slider.value()}")
        self.status.setText(f"{slider.title} set to {slider.value():g}")

    def restore_ramp(self, slider: MotionSlider, command: str) -> None:
        if slider.initial is None:
            return
        slider.set_value(slider.initial)
        self.apply_ramp(slider, command)

    def restore_initial_settings(self) -> None:
        """Send back the values read at connection time (best effort)."""
        if self.stage is None:
            return
        for slider, command in self.settings:
            if slider.initial is None or slider.restored:
                continue
            try:
                self.stage.send(self.address, f"{command} 1 {slider.initial}")
            except (ConnectionFailure, RuntimeError, OSError):
                return
            slider.restored = True

    def values(self) -> list[float]:
        values: list[float] = []
        for row in range(LOOKUP_TABLE_SIZE):
            item = self.table.item(row, 0)
            values.append(float(item.text()) if item is not None else 0.0)
        return values

    def set_values(self, values: list[float]) -> None:
        self.table.blockSignals(True)
        for row, value in enumerate(values):
            item = self.table.item(row, 0)
            if item is not None:
                item.setText(f"{value:.4f}")
        self.table.blockSignals(False)
        self.plot.set_values(values)

    def refresh_plot(self) -> None:
        try:
            self.plot.set_values(self.values())
        except ValueError:
            self.status.setText("Invalid value: expected a float in [-1.0, 1.0]")

    def read_table(self) -> None:
        if self.stage is None:
            return
        try:
            self.set_values(read_lookup_table(self.stage, self.address))
            self.status.setText("Lookup table read from controller")
        except ProtocolError as exc:
            QMessageBox.critical(self, f"Address {self.address}: read failed", str(exc))

    def load_default(self, table_type: int) -> None:
        if self.stage is None:
            return
        if not self.confirm_write():
            return
        load_default_lookup_table(self.stage, self.address, table_type)
        self.read_table()

    def write_table(self) -> None:
        if self.stage is None:
            return
        if not self.confirm_write():
            return
        try:
            write_lookup_table(self.stage, self.address, self.values())
            self.status.setText("Lookup table written to controller")
        except ValueError as exc:
            QMessageBox.critical(
                self, f"Address {self.address}: write failed", str(exc)
            )

    def confirm_write(self) -> bool:
        answer = QMessageBox.warning(
            self,
            "Write lookup table",
            "This writes to non-volatile memory, which supports a limited "
            "number of write cycles. Continue?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return answer == QMessageBox.StandardButton.Ok


class PILookupWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PI joystick lookup table")
        self.stage: PI | None = None
        self.tabs: dict[int, PILookupTab] = {}
        self.velocity_divisor = 1
        self.master_button_pressed = False

        layout = QVBoxLayout()
        self.setLayout(layout)

        box = QHBoxLayout()
        layout.addLayout(box)
        box.addWidget(QLabel("Port"))
        self.port_selection = QComboBox()
        self.port_selection.addItem("Auto detection", None)
        for port in comports():
            self.port_selection.addItem(port.device, userData=port)
        box.addWidget(self.port_selection)
        box.addWidget(QLabel("Addresses"))
        self.address_checks: list[QCheckBox] = []
        for address in (1, 2, 3):
            checkbox = QCheckBox(str(address))
            checkbox.setChecked(True)
            self.address_checks.append(checkbox)
            box.addWidget(checkbox)
        self.connect_button = QPushButton("Connect")
        self.connect_button.setCheckable(True)
        self.connect_button.clicked.connect(self.connect)
        box.addWidget(self.connect_button)
        self.home_button = QPushButton("Home")
        self.home_button.setEnabled(False)
        self.home_button.clicked.connect(self.home)
        box.addWidget(self.home_button)

        self.tab_widget = QTabWidget()
        self.tab_widget.setEnabled(False)
        layout.addWidget(self.tab_widget)

        warning = QLabel(
            "Writing stores the table in non-volatile memory, which supports a "
            "limited number of write cycles."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)

        self.joystick_button_poll_timer = QTimer()
        self.joystick_button_poll_timer.timeout.connect(self.poll_joystick_buttons)

    def selected_addresses(self) -> list[int]:
        return [
            address
            for address, checkbox in enumerate(self.address_checks, start=1)
            if checkbox.isChecked()
        ]

    def connect(self, on_off: bool) -> None:
        if not on_off:
            self.disconnect_stage()
            return
        addresses = self.selected_addresses()
        if not addresses:
            self.connect_button.setChecked(False)
            QMessageBox.warning(
                self,
                "No address selected",
                "Select at least one controller address.",
            )
            return
        try:
            port = self.port_selection.currentData()
            dev = port.device if isinstance(port, ListPortInfo) else None
            self.stage = PI(dev, addresses=addresses)
            self.tab_widget.clear()
            self.tabs.clear()
            for index, address in enumerate(addresses):
                tab = PILookupTab(address, index)
                tab.lookup_window = self
                tab.bind_stage(self.stage)
                self.tabs[address] = tab
                self.tab_widget.addTab(tab, f"Address {address}")
            self.velocity_divisor = 1
            # Recorded so that a button already held at connection time does
            # not count as a press.
            self.master_button_pressed = self.button_states().get(
                BUTTON_JOYSTICK_MASTER_ADDRESS, False
            )
            self.set_connected(True)
        except (ConnectionFailure, ProtocolError, ValueError, RuntimeError) as exc:
            self.disconnect_stage()
            self.connect_button.setChecked(False)
            QMessageBox.critical(self, "Connection failed", str(exc))

    def disconnect_stage(self) -> None:
        self.joystick_button_poll_timer.stop()
        for tab in self.tabs.values():
            tab.unbind_stage()
        self.tab_widget.clear()
        self.tabs.clear()
        self.stage = None
        self.velocity_divisor = 1
        self.master_button_pressed = False
        self.set_connected(False)

    def set_connected(self, connected: bool) -> None:
        self.port_selection.setDisabled(connected)
        for checkbox in self.address_checks:
            checkbox.setDisabled(connected)
        self.tab_widget.setEnabled(connected)
        self.home_button.setEnabled(connected)
        if connected:
            self.joystick_button_poll_timer.start(100)

    def home(self) -> None:
        if self.stage is None:
            return
        answer = QMessageBox.warning(
            self,
            "Home",
            "This moves every connected axis to the negative limit switch. "
            "Make sure the path is clear. Continue?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Ok:
            return
        self.home_button.setEnabled(False)
        try:
            self.stage.home(wait=True)
        except (ConnectionFailure, ProtocolError, RuntimeError) as exc:
            QMessageBox.critical(self, "Home failed", str(exc))
        else:
            for tab in self.tabs.values():
                tab.status.setText("Homing finished")
        finally:
            self.home_button.setEnabled(True)

    def button_states(self) -> dict[int, bool]:
        """Pressed state of the joystick button of each connected address."""
        assert self.stage is not None
        buttons = self.stage.joystick_buttons
        return {
            address: buttons[tab.address_index] for address, tab in self.tabs.items()
        }

    def apply_all_velocities(self) -> None:
        if self.stage is None:
            return
        self.stage.velocity = [
            tab.velocity.value() / self.velocity_divisor for tab in self.tabs.values()
        ]

    def toggle_all_joysticks(self) -> None:
        """Master button press enables or disables the joystick on every axis."""
        if self.stage is None:
            return
        try:
            self.stage.joystick_enabled = not self.stage.joystick_enabled[0]
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            return
        for tab in self.tabs.values():
            tab.sync_joystick_state()

    def poll_joystick_buttons(self) -> None:
        if self.stage is None:
            return
        try:
            states = self.button_states()
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            return

        for address, tab in self.tabs.items():
            tab.show_button(states.get(address, False))

        divisor = next(
            (
                d
                for address, d in BUTTON_VELOCITY_DIVISOR.items()
                if states.get(address)
            ),
            1,
        )
        if divisor != self.velocity_divisor:
            self.velocity_divisor = divisor
            self.apply_all_velocities()

        pressed = states.get(BUTTON_JOYSTICK_MASTER_ADDRESS, False)
        if pressed and not self.master_button_pressed:
            self.toggle_all_joysticks()
        self.master_button_pressed = pressed

    def restore_initial_settings(self) -> None:
        for tab in self.tabs.values():
            tab.restore_initial_settings()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.disconnect_stage()
        super().closeEvent(a0)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PI joystick lookup table")
    window = PILookupWindow()

    def cleanup() -> None:
        window.restore_initial_settings()

    app.aboutToQuit.connect(cleanup)
    atexit.register(cleanup)

    def signal_handler(signum: int, _frame: object | None) -> None:
        cleanup()
        sys.exit(128 + signum)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    window.resize(520, 760)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
