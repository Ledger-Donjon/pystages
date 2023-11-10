#!/bin/python3
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
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

    def __init__(self):
        super().__init__()

        # Current stage
        self.stage: Stage = None

        box = QHBoxLayout()
        w = QLabel("Stage Selection")
        box.addWidget(w)
        self.stage_selection = w = QComboBox()
        w.addItems([StageType.CNC, StageType.Corvus, StageType.SMC])

        box.addWidget(w)
        self.setLayout(box)

        self.connect_button = w = QPushButton("Connect")
        w.setCheckable(True)
        w.clicked.connect(self.connect)
        box.addWidget(w)
