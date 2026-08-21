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

import sys

from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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


def read_lookup_table(stage: PI, address: int) -> list[float]:
    """Read the 256 velocity factors of the joystick lookup table (``JLT?``)."""
    query = f"{address} JLT? 1 {LOOKUP_TABLE_SIZE}"
    stage.serial.write(f"{query}\n".encode("utf-8"))
    values: list[float] = []
    in_header = True
    while len(values) < LOOKUP_TABLE_SIZE:
        line = stage.serial.readline().decode("utf-8").strip()
        if not line:
            break
        if in_header:
            in_header = not line.upper().endswith("END HEADER")
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

    def paintEvent(self, event) -> None:  # type: ignore[override]
        _ = event
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


class PILookupWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PI joystick lookup table")
        self.stage: PI | None = None

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
        box.addWidget(QLabel("Address"))
        self.address_edit = QLineEdit("1")
        box.addWidget(self.address_edit)
        self.connect_button = QPushButton("Connect")
        self.connect_button.setCheckable(True)
        self.connect_button.clicked.connect(self.connect)
        box.addWidget(self.connect_button)

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
        self.buttons = []
        for label, slot in (
            ("Read", self.read_table),
            ("Linear", lambda: self.load_default(LINEAR)),
            ("Parabolic", lambda: self.load_default(PARABOLIC)),
            ("Write", self.write_table),
        ):
            button = QPushButton(label)
            button.clicked.connect(slot)
            button.setEnabled(False)
            box.addWidget(button)
            self.buttons.append(button)

        warning = QLabel(
            "Writing stores the table in non-volatile memory, which supports a "
            "limited number of write cycles."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)
        self.status = QLabel("Disconnected")
        layout.addWidget(self.status)

    def connect(self, on_off: bool) -> None:
        if not on_off:
            self.stage = None
            self.set_connected(False)
            self.status.setText("Disconnected")
            return
        try:
            port = self.port_selection.currentData()
            dev = port.device if isinstance(port, ListPortInfo) else None
            address = int(self.address_edit.text())
            self.stage = PI(dev, addresses=[address])
            self.set_connected(True)
            self.status.setText(f"Connected to controller {address}")
            self.read_table()
        except (ConnectionFailure, ProtocolError, ValueError, RuntimeError) as exc:
            self.stage = None
            self.connect_button.setChecked(False)
            self.set_connected(False)
            self.status.setText("Disconnected")
            QMessageBox.critical(self, "Connection failed", str(exc))

    def set_connected(self, connected: bool) -> None:
        self.port_selection.setDisabled(connected)
        self.address_edit.setDisabled(connected)
        for button in self.buttons:
            button.setEnabled(connected)

    def address(self) -> int:
        assert self.stage is not None
        return self.stage.addresses[0]

    def values(self) -> list[float]:
        values = []
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
            self.set_values(read_lookup_table(self.stage, self.address()))
            self.status.setText("Lookup table read from controller")
        except ProtocolError as exc:
            QMessageBox.critical(self, "Read failed", str(exc))

    def load_default(self, table_type: int) -> None:
        if self.stage is None:
            return
        if not self.confirm_write():
            return
        load_default_lookup_table(self.stage, self.address(), table_type)
        self.read_table()

    def write_table(self) -> None:
        if self.stage is None:
            return
        if not self.confirm_write():
            return
        try:
            write_lookup_table(self.stage, self.address(), self.values())
            self.status.setText("Lookup table written to controller")
        except ValueError as exc:
            QMessageBox.critical(self, "Write failed", str(exc))

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


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PI joystick lookup table")
    window = PILookupWindow()
    window.resize(480, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
