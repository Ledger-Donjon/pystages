#!/bin/python3
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
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
        self.position_label = w = QLabel("Pos")
        vbox.addWidget(w)
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)

    def update_position(self):
        if self.stage is None or self.in_motion:
            return
        position = self.stage.position
        self.position_label.setText(",".join([f"{i:.02f}" for i in position.data]))
