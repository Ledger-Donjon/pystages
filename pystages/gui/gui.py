#!/bin/python3
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QCheckBox,
    QLineEdit,
)
from PyQt6.QtCore import QObject, QTimer, QLocale, QCoreApplication
from PyQt6.QtGui import QDoubleValidator
from ..cncrouter import CNCRouter
from ..corvus import Corvus
from ..smc100 import SMC100
from ..stage import Stage
from enum import Enum
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo


class StageType(str, Enum):
    CNC = "CNC"
    Corvus = "Corvus"
    SMC = "SMC100"


class StageWindow(QWidget):
    def set_controls_enabled(self, enabled: bool):
        for c in self.controls:
            c.setEnabled(enabled)

    def connect(self, on_off):
        if on_off:
            selected = self.stage_selection.currentText()
            port = self.port_selection.currentData()
            dev = port.device if isinstance(port, ListPortInfo) else None

            # Instanciate stage according to current stage selection
            if selected == StageType.CNC:
                self.stage = CNCRouter(dev)
            elif selected == StageType.Corvus:
                self.stage = Corvus(dev)
            elif selected == StageType.SMC:
                self.stage = SMC100(dev, [1, 2])
            self.position_timer.start(100)

        else:
            del self.stage
            self.stage = None

            self.position_timer.stop()

        self.stage_selection.setDisabled(on_off)
        self.port_selection.setDisabled(on_off)

        self.set_controls_enabled(on_off)

        if self.stage is not None:
            self.stage.wait_routine = lambda: QCoreApplication.processEvents()

    def __init__(self):
        super().__init__()

        # Current stage
        self.stage: Optional[Stage] = None

        # This flag is used to limit the communication
        # with the stage by not making updates of the position
        self.in_motion = False

        # Moving controls
        self.controls = []

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        box = QHBoxLayout()
        vbox.addLayout(box)
        w = QLabel("Stage Selection")
        box.addWidget(w)
        self.stage_selection = w = QComboBox()
        w.addItems([StageType.CNC, StageType.Corvus, StageType.SMC])
        box.addWidget(w)
        self.port_selection = w = QComboBox()
        w.addItem("Auto detection", None)
        for port in comports():
            d = port.device
            if port.vid and port.pid:
                d += f" -- {port.vid:04x}:{port.pid:04x}"
            if port.product:
                d += f" -- {port.product}"
            if port.serial_number:
                d += f" -- {port.serial_number}"
            w.addItem(d, userData=port)
        box.addWidget(w)
        self.connect_button = w = QPushButton("Connect")
        w.setCheckable(True)
        w.clicked.connect(self.connect)
        box.addWidget(w)

        box = QHBoxLayout()
        vbox.addLayout(box)
        box.addWidget(QLabel("Step"))
        self.step_selection = w = QComboBox()
        for step in [50, 10, 5, 1, 0.5, 0.1]:
            w.addItem(f"{step} mm", step)
        w.setCurrentIndex(3)
        box.addWidget(w)
        self.controls.append(w)

        self.moving_grid = grid = QGridLayout()
        w = QPushButton("Y+")
        w.clicked.connect(self.bouton_moved)
        self.controls.append(w)
        grid.addWidget(w, 0, 1)
        w = QPushButton("X-")
        w.clicked.connect(self.bouton_moved)
        self.controls.append(w)
        grid.addWidget(w, 1, 0)
        w = QPushButton("Y-")
        w.clicked.connect(self.bouton_moved)
        self.controls.append(w)
        grid.addWidget(w, 2, 1)
        w = QPushButton("X+")
        w.clicked.connect(self.bouton_moved)
        self.controls.append(w)
        grid.addWidget(w, 1, 2)
        w = QPushButton("Z+")
        w.clicked.connect(self.bouton_moved)
        self.controls.append(w)
        grid.addWidget(w, 0, 3)
        w = QPushButton("Z-")
        w.clicked.connect(self.bouton_moved)
        self.controls.append(w)
        grid.addWidget(w, 2, 3)
        w = QPushButton("Home")
        w.clicked.connect(self.home)
        self.controls.append(w)
        grid.addWidget(w, 1, 1)
        vbox.addLayout(grid)

        box = QHBoxLayout()
        vbox.addLayout(box)
        self.z_offset = w = QCheckBox("Z offset (mm)")
        w.setChecked(True)
        box.addWidget(w)
        self.controls.append(w)
        self.z_offset_sel = w = QComboBox()
        for value in [10, 5, 1, 0.5, 0.1]:
            w.addItem(f"{value} mm", value)
        w.setCurrentIndex(2)
        box.addWidget(w)
        self.controls.append(w)

        v = QDoubleValidator()
        v.setLocale(QLocale.c())
        box = QHBoxLayout()
        vbox.addLayout(box)
        self.go_x = w = QLineEdit()
        w.setValidator(v)
        box.addWidget(w)
        self.go_y = w = QLineEdit()
        w.setValidator(v)
        box.addWidget(w)
        self.go_z = w = QLineEdit()
        w.setValidator(v)
        box.addWidget(w)
        w = QPushButton("Go to position")
        w.clicked.connect(self.go_to_position)
        self.controls.append(w)
        box.addWidget(w)

        # Disable all controls
        self.set_controls_enabled(False)

        self.position_label = w = QLabel("Pos")
        vbox.addWidget(w)
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)

    def update_position(self):
        if self.stage is None or self.in_motion:
            return
        position = self.stage.position
        self.position_label.setText(",".join([f"{i:.02f}" for i in position.data]))

    def bouton_moved(self):
        if self.stage is None:
            return
        self.in_motion = True
        button = QObject().sender()
        assert isinstance(button, QPushButton)
        axe, direction = button.text()
        axe = {"X": 0, "Y": 1, "Z": 2}[axe]
        direction = {"+": 1.0, "-": -1.0}[direction]
        step = direction * self.step_selection.currentData()
        pos = self.stage.position
        z_offset = (
            self.z_offset_sel.currentData()
            if axe != 2 and self.z_offset.isChecked()
            else None
        )

        if z_offset is not None:
            pos[2] += z_offset
            self.stage.move_to(pos)

        pos[axe] += step
        self.stage.move_to(pos)

        if z_offset is not None:
            pos[2] -= z_offset
            self.stage.move_to(pos)
        self.in_motion = False

    def home(self):
        if self.stage is None:
            return
        self.stage.home(wait=True)

    def go_to_position(self):
        if self.stage is None:
            return
        x, y, z = (
            QLocale.c().toDouble(self.go_x.text())[0],
            QLocale.c().toDouble(self.go_y.text())[0],
            QLocale.c().toDouble(self.go_z.text())[0],
        )
        pos = self.stage.position
        pos.x = x
        pos.y = y
        pos.z = z
        self.stage.move_to(pos)
