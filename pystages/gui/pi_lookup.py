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

from PyQt6.QtCore import Qt, QTimer
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
from ..pi import PI, PI_MIN_CLOSED_LOOP_VELOCITY, PIVelocityLimits

LOOKUP_TABLE_SIZE = 256
LINEAR = 1
PARABOLIC = 2
# Number of table points sent per JLT command.
WRITE_CHUNK = 16
VELOCITY_SLIDER_SCALE = 100
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


def enable_joystick_address(stage: PI, address: int) -> None:
    stage.send(address, "JAX 1 1 1")
    stage.send(address, "JON 1 1")


def disable_joystick_address(stage: PI, address: int) -> None:
    stage.send(address, "JON 1 0")


def set_velocity_address(stage: PI, address: int, velocity: float) -> None:
    stage.send(address, f"VEL 1 {velocity}")


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


class PILookupTab(QWidget):
    """Controls for one controller address."""

    def __init__(self, address: int, address_index: int) -> None:
        super().__init__()
        self.address = address
        self.address_index = address_index
        self.stage: PI | None = None
        self._initial_velocity: float | None = None
        self._velocity_limits: PIVelocityLimits | None = None
        self._velocity_restored = True
        self._slider_maximum = 0.01
        self.lookup_window: PILookupWindow | None = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        box = QHBoxLayout()
        layout.addLayout(box)
        box.addWidget(QLabel("Velocity"))
        self.velocity_slider = QSlider(Qt.Orientation.Horizontal)
        self.velocity_slider.valueChanged.connect(self._update_velocity_label)
        self.velocity_slider.sliderReleased.connect(self.apply_velocity)
        box.addWidget(self.velocity_slider, stretch=1)
        self.velocity_value_label = QLabel("—")
        self.velocity_value_label.setMinimumWidth(48)
        box.addWidget(self.velocity_value_label)
        self.velocity_restore_button = QPushButton("Restore initial")
        self.velocity_restore_button.clicked.connect(self.restore_initial_velocity)
        box.addWidget(self.velocity_restore_button)
        self.initial_velocity_label = QLabel("")
        box.addWidget(self.initial_velocity_label)

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
        self._update_joystick_ui(False)
        self._update_physical_button_indicator(False, connected=False)

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
        limits = stage.velocity_limits[self.address_index]
        self._initial_velocity = stage.velocity[self.address_index]
        self._velocity_limits = limits
        self._configure_velocity_slider(limits, self._initial_velocity)
        self._velocity_restored = False
        self._set_velocity_slider_value(self._clamp_velocity(self._initial_velocity))
        self.initial_velocity_label.setText(
            f"(initial: {self._initial_velocity:g}, "
            f"range: 0–{self._slider_maximum:g}, default: {limits.default:g})"
        )
        self.sync_joystick_state()
        self.sync_invert_direction()
        self.read_table()
        self.status.setText(f"Connected to controller {self.address}")

    def unbind_stage(self) -> None:
        self.restore_velocity()
        self.stage = None
        self._initial_velocity = None
        self._velocity_limits = None
        self.initial_velocity_label.setText("")
        self._reset_velocity_slider()
        self._update_joystick_ui(False)
        self._update_physical_button_indicator(False, connected=False)
        self.invert_direction_checkbox.blockSignals(True)
        self.invert_direction_checkbox.setChecked(False)
        self.invert_direction_checkbox.blockSignals(False)
        self.lookup_window = None
        self.status.setText("Disconnected")

    def _configure_velocity_slider(
        self, limits: PIVelocityLimits, current: float
    ) -> None:
        maximum = max(limits.maximum, current, 0.01)
        self.velocity_slider.setRange(
            round(PI_MIN_CLOSED_LOOP_VELOCITY * VELOCITY_SLIDER_SCALE),
            round(maximum * VELOCITY_SLIDER_SCALE),
        )
        self._slider_maximum = maximum

    def _clamp_velocity(self, velocity: float) -> float:
        return min(self._slider_maximum, max(PI_MIN_CLOSED_LOOP_VELOCITY, velocity))

    def _slider_velocity(self) -> float:
        return self.velocity_slider.value() / VELOCITY_SLIDER_SCALE

    def _set_velocity_slider_value(self, velocity: float) -> None:
        self.velocity_slider.blockSignals(True)
        self.velocity_slider.setValue(round(velocity * VELOCITY_SLIDER_SCALE))
        self.velocity_slider.blockSignals(False)
        self._update_velocity_label()

    def _update_velocity_label(self, _value: int | None = None) -> None:
        self.velocity_value_label.setText(f"{self._slider_velocity():g}")

    def _reset_velocity_slider(self) -> None:
        self.velocity_slider.blockSignals(True)
        self.velocity_slider.setRange(0, VELOCITY_SLIDER_SCALE)
        self.velocity_slider.setValue(0)
        self.velocity_slider.blockSignals(False)
        self.velocity_value_label.setText("—")

    def _update_joystick_ui(self, enabled: bool) -> None:
        self.joystick_button.blockSignals(True)
        self.joystick_button.setChecked(enabled)
        self.joystick_button.setText(
            "Joystick enabled" if enabled else "Joystick disabled"
        )
        self.joystick_button.blockSignals(False)

    def _update_physical_button_indicator(
        self, pressed: bool, *, connected: bool = True
    ) -> None:
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
            enabled = self.stage.joystick_enabled[self.address_index]
            self._update_joystick_ui(enabled)
        except ProtocolError as exc:
            QMessageBox.critical(
                self, f"Address {self.address}: joystick state read failed", str(exc)
            )

    def toggle_joystick(self, enabled: bool) -> None:
        if self.stage is None:
            return
        try:
            if enabled:
                enable_joystick_address(self.stage, self.address)
                self.status.setText("Joystick enabled")
            else:
                disable_joystick_address(self.stage, self.address)
                self.status.setText("Joystick disabled")
            self._update_joystick_ui(enabled)
        except ProtocolError as exc:
            self._update_joystick_ui(not enabled)
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
        if self.stage is None or self.lookup_window is None:
            return
        base = self._slider_velocity()
        try:
            self.lookup_window.apply_all_velocities()
            divisor = self.lookup_window.velocity_divisor
            if divisor > 1:
                self.status.setText(
                    f"Velocity set to {base:g} ({base / divisor:g} active on all axes)"
                )
            else:
                self.status.setText(f"Velocity set to {base:g}")
        except ProtocolError as exc:
            QMessageBox.critical(
                self, f"Address {self.address}: velocity update failed", str(exc)
            )

    def restore_initial_velocity(self) -> None:
        if (
            self.stage is None
            or self._initial_velocity is None
            or self._velocity_limits is None
            or self.lookup_window is None
        ):
            return
        try:
            self._set_velocity_slider_value(
                self._clamp_velocity(self._initial_velocity)
            )
            self.lookup_window.apply_all_velocities()
            self.status.setText(f"Velocity restored to {self._initial_velocity:g}")
        except ProtocolError as exc:
            QMessageBox.critical(
                self, f"Address {self.address}: velocity restore failed", str(exc)
            )

    def restore_velocity(self) -> None:
        """Restore the velocity read at connection time (best effort)."""
        if (
            self._velocity_restored
            or self.stage is None
            or self._initial_velocity is None
        ):
            return
        try:
            set_velocity_address(self.stage, self.address, self._initial_velocity)
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            pass
        else:
            self._velocity_restored = True

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
        self._addr3_button_pressed = False
        self._button_states: dict[int, bool] = {}

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
            self._addr3_button_pressed = False
            self._button_states = {}
            self.sync_physical_buttons()
            self._sync_addr3_button_state()
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
        self._addr3_button_pressed = False
        self._button_states = {}
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

    @staticmethod
    def _velocity_divisor_from_buttons(states: dict[int, bool]) -> int:
        if states.get(1, False):
            return BUTTON_VELOCITY_DIVISOR[1]
        if states.get(2, False):
            return BUTTON_VELOCITY_DIVISOR[2]
        return 1

    def _read_button_states(self) -> dict[int, bool]:
        assert self.stage is not None
        buttons = self.stage.joystick_buttons
        return {
            address: buttons[tab.address_index] for address, tab in self.tabs.items()
        }

    def apply_all_velocities(self) -> None:
        if self.stage is None:
            return
        for tab in self.tabs.values():
            velocity = tab._slider_velocity() / self.velocity_divisor
            set_velocity_address(self.stage, tab.address, velocity)

    def _set_all_joysticks_enabled(self, enabled: bool) -> None:
        assert self.stage is not None
        for tab in self.tabs.values():
            if enabled:
                enable_joystick_address(self.stage, tab.address)
            else:
                disable_joystick_address(self.stage, tab.address)
            tab.sync_joystick_state()

    def _toggle_all_joysticks(self) -> None:
        if self.stage is None or not self.tabs:
            return
        first_tab = next(iter(self.tabs.values()))
        try:
            enabled = self.stage.joystick_enabled[first_tab.address_index]
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            return
        self._set_all_joysticks_enabled(not enabled)

    def sync_physical_buttons(self) -> None:
        if self.stage is None:
            return
        try:
            states = self._read_button_states()
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            return
        for address, tab in self.tabs.items():
            tab._update_physical_button_indicator(states.get(address, False))
        self.velocity_divisor = self._velocity_divisor_from_buttons(states)
        self.apply_all_velocities()
        self._button_states = states

    def _sync_addr3_button_state(self) -> None:
        """Record address-3 button state without triggering a toggle."""
        if self.stage is None:
            return
        try:
            states = self._read_button_states()
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            return
        self._addr3_button_pressed = states.get(BUTTON_JOYSTICK_MASTER_ADDRESS, False)

    def poll_joystick_buttons(self) -> None:
        if self.stage is None:
            return
        try:
            states = self._read_button_states()
        except (ProtocolError, ConnectionFailure, RuntimeError, OSError):
            return

        for address, tab in self.tabs.items():
            tab._update_physical_button_indicator(states.get(address, False))

        divisor = self._velocity_divisor_from_buttons(states)
        if divisor != self.velocity_divisor:
            self.velocity_divisor = divisor
            self.apply_all_velocities()

        if BUTTON_JOYSTICK_MASTER_ADDRESS in self.tabs:
            master_pressed = states.get(BUTTON_JOYSTICK_MASTER_ADDRESS, False)
            if master_pressed and not self._addr3_button_pressed:
                self._toggle_all_joysticks()
            self._addr3_button_pressed = master_pressed

        self._button_states = states

    def restore_velocity(self) -> None:
        for tab in self.tabs.values():
            tab.restore_velocity()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.disconnect_stage()
        super().closeEvent(a0)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PI joystick lookup table")
    window = PILookupWindow()

    def cleanup() -> None:
        window.restore_velocity()

    app.aboutToQuit.connect(cleanup)
    atexit.register(cleanup)

    def signal_handler(signum: int, _frame: object | None) -> None:
        cleanup()
        sys.exit(128 + signum)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    window.resize(480, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
