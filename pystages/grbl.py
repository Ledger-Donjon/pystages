# This file is part of pystages
#
# pystages is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Values and descriptions of commands and error codes has been taken from GRBL Github repository
# https://github.com/grbl/grbl
# and the instruction manual of the CNC 3018 PRO
# https://drive.google.com/file/d/1yQH9gtO8lWbE-K0dff8g9zq_1xOB57x7
#
# Copyright 2018-2022 Ledger SAS, written by Michaël Mouchous
from enum import Enum, Flag
from typing import Union


class InvertMask(Flag):
    """
    Invert Mask flags values
    """

    INVERT_X = 1
    INVERT_Y = 1 << 1
    INVERT_Z = 1 << 2


class StatusReportMask(Flag):
    """
    Status report flags values
    """

    NOTHING = 0
    MACHINE_POSITION = 1
    WORK_POSITION = 1 << 1
    PLANNER_BUFFER = 1 << 2
    RX_BUFFER = 1 << 3
    LIMIT_PINS = 1 << 4


class GRBLSetting(Enum):
    """
    GRBL Setting are obtained by sending the '$$' command as a list of
    key-value pairs '$K=V' with K being a number.
    """

    STEP_PULSE = "$0"
    STEP_IDLE_DELAY = "$1"
    STEP_PORT_INVERT = "$2"
    DIR_PORT_INVERT = "$3"
    STEP_ENABLE_INVERT = "$4"
    LIMIT_PINS_INVERT = "$5"
    PROBE_PIN_INVERT = "$6"
    STATUS_REPORT_MASK = "$10"
    JUNCTION_DEVIATION = "$11"
    ARC_TOLERANCE = "$12"
    REPORT_INCHES = "$13"
    SOFT_LIMITS = "$20"
    HARD_LIMITS = "$21"
    HOMING_CYCLE = "$22"
    HOMING_DIR_INVERT = "$23"
    HOMING_FEED = "$24"
    HOMING_SEEK = "$25"
    HOMING_DEBOUNCE = "$26"
    HOMING_PULL_OFF = "$27"
    SPINDLE_RPM_MAX = "$30"
    SPINDLE_RPM_MIN = "$31"
    LASER_MODE = "$32"
    STEPS_PER_MM_X = "$100"
    STEPS_PER_MM_Y = "$101"
    STEPS_PER_MM_Z = "$102"
    MAX_RATE_X = "$110"
    MAX_RATE_Y = "$111"
    MAX_RATE_Z = "$112"
    ACCELERATION_X = "$120"
    ACCELERATION_Y = "$121"
    ACCELERATION_Z = "$122"
    MAX_TRAVEL_X = "$130"
    MAX_TRAVEL_Y = "$131"
    MAX_TRAVEL_Z = "$132"

    @property
    def type(self) -> type:
        """
        Gives the type of the value stored in the GRBL setting
        """
        return type(self._description[0])

    @property
    def default_value(self) -> Union[float, bool, InvertMask, StatusReportMask, int]:
        """
        Gives the default value of the GRBL setting
        """
        return self._description[0]

    @property
    def description(self) -> str:
        """
        Gives the string description of the GRBL setting
        """
        return self._description[1]

    @property
    def _description(self) -> dict:
        # Numbering: (type, default value, description)
        return {
            GRBLSetting.STEP_PULSE: (10.0, "Step pulse, usec"),
            GRBLSetting.STEP_IDLE_DELAY: (25.0, "Step idle delay, msec"),
            GRBLSetting.STEP_PORT_INVERT: (InvertMask(0), "Step port invert"),
            GRBLSetting.DIR_PORT_INVERT: (InvertMask(6), "Direction port invert"),
            GRBLSetting.STEP_ENABLE_INVERT: (False, "Step enable invert"),
            GRBLSetting.LIMIT_PINS_INVERT: (False, "Limit pins invert"),
            GRBLSetting.PROBE_PIN_INVERT: (False, "Probe pin invert"),
            GRBLSetting.STATUS_REPORT_MASK: (StatusReportMask(3), "Status report mask"),
            GRBLSetting.JUNCTION_DEVIATION: (0.020, "Junction deviation, mm"),
            GRBLSetting.ARC_TOLERANCE: (0.002, "Arc tolerance, mm"),
            GRBLSetting.REPORT_INCHES: (False, "Report inches"),
            GRBLSetting.SOFT_LIMITS: (False, "Soft limits"),
            GRBLSetting.HARD_LIMITS: (False, "Hard limits"),
            GRBLSetting.HOMING_CYCLE: (False, "Homing cycle"),
            GRBLSetting.HOMING_DIR_INVERT: (InvertMask(1), "Homing dir invert"),
            GRBLSetting.HOMING_FEED: (50.000, "Homing feed, mm/min"),
            GRBLSetting.HOMING_SEEK: (635.000, "Homing seek, mm/min"),
            GRBLSetting.HOMING_DEBOUNCE: (250.0, "Homing debounce, msec"),
            GRBLSetting.HOMING_PULL_OFF: (1.000, "Homing pull-off, mm"),
            GRBLSetting.STEPS_PER_MM_X: (800.0, "X steps/mm"),
            GRBLSetting.STEPS_PER_MM_Y: (800.0, "Y steps/mm"),
            GRBLSetting.STEPS_PER_MM_Z: (800.0, "Z steps/mm"),
            GRBLSetting.MAX_RATE_X: (635.000, "X max rate, mm/min"),
            GRBLSetting.MAX_RATE_Y: (635.000, "Y max rate, mm/min"),
            GRBLSetting.MAX_RATE_Z: (635.000, "Z max rate, mm/min"),
            GRBLSetting.ACCELERATION_X: (50.000, "X acceleration, mm/sec^2"),
            GRBLSetting.ACCELERATION_Y: (50.000, "Y acceleration, mm/sec^2"),
            GRBLSetting.ACCELERATION_Z: (50.000, "Z acceleration, mm/sec^2"),
            GRBLSetting.MAX_TRAVEL_X: (225.000, "X max travel, mm"),
            GRBLSetting.MAX_TRAVEL_Y: (125.000, "Y max travel, mm"),
            GRBLSetting.MAX_TRAVEL_Z: (170.000, "Z max travel, mm"),
            GRBLSetting.SPINDLE_RPM_MAX: (
                1000.0,
                "Spindle maximal rotation speed, rpm",
            ),
            GRBLSetting.SPINDLE_RPM_MIN: (0.0, "Spindle minimal rotation speed, rpm"),
            GRBLSetting.LASER_MODE: (False, "Laser mode activated"),
        }[self]

    def __str__(self):
        return f"{self.description}: (default value: {self.type(self.default_value)})"
