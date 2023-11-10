#!/bin/python3
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QCheckBox,
)
from PyQt6.QtCore import QObject, QTimer
from ..cncrouter import CNCRouter
from ..corvus import Corvus
from ..smc100 import SMC100
from ..stage import Stage
from enum import Enum


class StageType(str, Enum):
    CNC = "CNC"
    Corvus = "Corvus"
    SMC = "SMC100"


class StageWindow(QWidget):
    def connect(self, on_off):
        print(on_off, selected := self.stage_selection.currentText())
        if on_off:
            # Instanciate stage according to current stage selection
            if selected == StageType.CNC:
                self.stage = CNCRouter()
            elif selected == StageType.Corvus:
                self.stage = Corvus()
            elif selected == StageType.SMC:
                self.stage = SMC100()
            self.position_timer.start(100)
        else:
            del self.stage
            self.stage = None
            self.position_timer.stop()

    def __init__(self):
        super().__init__()

        # Current stage
        self.stage: Stage = None

        # This flag is used to limit the communication
        # with the stage by not making updates of the position
        self.in_motion = False

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        box = QHBoxLayout()
        vbox.addLayout(box)
        w = QLabel("Stage Selection")
        box.addWidget(w)
        self.stage_selection = w = QComboBox()
        w.addItems([StageType.CNC, StageType.Corvus, StageType.SMC])
        box.addWidget(w)
        self.connect_button = w = QPushButton("Connect")
        w.setCheckable(True)
        w.clicked.connect(self.connect)
        box.addWidget(w)

        box = QHBoxLayout()
        vbox.addLayout(box)
        box.addWidget(QLabel("Step (mm)"))
        self.step_selection = w = QComboBox()
        w.addItems(["10", "5", "1", "0.5", "0.1"])
        w.setCurrentText("1")
        box.addWidget(w)

        grid = QGridLayout()
        w = QPushButton("Y+")
        w.clicked.connect(self.bouton_moved)
        grid.addWidget(w, 0, 1)
        w = QPushButton("X-")
        w.clicked.connect(self.bouton_moved)
        grid.addWidget(w, 1, 0)
        w = QPushButton("Y-")
        w.clicked.connect(self.bouton_moved)
        grid.addWidget(w, 2, 1)
        w = QPushButton("X+")
        w.clicked.connect(self.bouton_moved)
        grid.addWidget(w, 1, 2)
        w = QPushButton("Z+")
        w.clicked.connect(self.bouton_moved)
        grid.addWidget(w, 0, 3)
        w = QPushButton("Z-")
        w.clicked.connect(self.bouton_moved)
        grid.addWidget(w, 2, 3)
        vbox.addLayout(grid)

        box = QHBoxLayout()
        vbox.addLayout(box)
        self.z_offset = w = QCheckBox("Z offset (mm)")
        w.setChecked(True)
        box.addWidget(w)
        self.z_offset_sel = w = QComboBox()
        w.addItems(["10", "5", "1", "0.5", "0.1"])
        w.setCurrentText("1")
        box.addWidget(w)

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
        axe, direction = button.text()
        axe = {"X": 0, "Y": 1, "Z": 2}[axe]
        step = float(direction + self.step_selection.currentText())
        pos = self.stage.position
        if axe != 2 and self.z_offset.isChecked():
            pos[2] += float(self.z_offset_sel.currentText())
            self.stage.move_to(pos)

        pos[axe] += step
        self.stage.move_to(pos)

        if axe != 2 and self.z_offset.isChecked():
            pos[2] -= float(self.z_offset_sel.currentText())
            self.stage.move_to(pos)
        self.in_motion = False
