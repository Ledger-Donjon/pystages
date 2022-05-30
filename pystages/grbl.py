from enum import Enum, Flag

GRBL_ALARM_DESC = {
    "ALARM:1": "Hard limit triggered. Machine position is likely lost due to sudden and immediate halt. Re-homing is highly recommended.",
    "ALARM:2": "G-code motion target exceeds machine travel. Machine position safely retained. Alarm may be unlocked.",
    "ALARM:3": "Reset while in motion. Grbl cannot guarantee position. Lost steps are likely. Re-homing is highly recommended.",
    "ALARM:4": "Probe fail. The probe is not in the expected initial state before starting probe cycle, where G38.2 and G38.3 is not triggered and G38.4 and G38.5 is triggered.",
    "ALARM:5": "Probe fail. Probe did not contact the workpiece within the programmed travel for G38.2 and G38.4.",
    "ALARM:6": "Homing fail. Reset during active homing cycle.",
    "ALARM:7": "Homing fail. Safety door was opened during active homing cycle.",
    "ALARM:8": "Homing fail. Cycle failed to clear limit switch when pulling off. Try increasing pull-off setting or check wiring.",
    "ALARM:9": "Homing fail. Could not find limit switch within search distance. Defined as 1.5 * max_travel on search and 5 * pulloff on locate phases.",
}
GRBL_HOLD_DESC = {
    "Hold:0": "Hold complete. Ready to resume.",
    "Hold:1": "Hold in-progress. Reset will throw an alarm.",
}
GRBL_DOOR_DESC = {
    "Door:0": "Door closed. Ready to resume.",
    "Door:1": "Machine stopped. Door still ajar. Can’t resume until closed.",
    "Door:2": "Door opened. Hold (or parking retract) in-progress. Reset will throw an alarm.",
    "Door:3": "Door closed and resuming. Restoring from park, if applicable. Reset will throw an alarm.",
}
GRBL_ERROR_DESC = {
    "error:1": "G-code words consist of a letter and a value. Letter was not found.",
    "error:2": "Numeric value format is not valid or missing an expected value.",
    "error:3": "Grbl '$' system command was not recognized or supported.",
    "error:4": "Negative value received for an expected positive value.",
    "error:5": "Homing cycle is not enabled via settings.",
    "error:6": "Minimum step pulse time must be greater than 3usec",
    "error:7": "EEPROM read failed. Reset and restored to default values.",
    "error:8": "Grbl '$' command cannot be used unless Grbl is IDLE. Ensures smooth operation during a job.",
    "error:9": "G-code locked out during alarm or jog state",
    "error:10": "Soft limits cannot be enabled without homing also enabled.",
    "error:11": "Max characters per line exceeded. Line was not processed and executed.",
    "error:12": "(Compile Option) Grbl '$' setting value exceeds the maximum step rate supported.",
    "error:13": "Safety door detected as opened and door state initiated.",
    "error:14": "(Grbl-Mega Only) Build info or startup line exceeded EEPROM line length limit.",
    "error:15": "Jog target exceeds machine travel. Command ignored.",
    "error:16": "Jog command with no '=' or contains prohibited g-code.",
    "error:20": "Unsupported or invalid g-code command found in block.",
    "error:21": "More than one g-code command from same modal group found in block.",
    "error:22": "Feed rate has not yet been set or is undefined.",
    "error:23": "G-code command in block requires an integer value.",
    "error:24": "Two G-code commands that both require the use of the XYZ axis words were detected in the block.",
    "error:25": "A G-code word was repeated in the block.",
    "error:26": "A G-code command implicitly or explicitly requires XYZ axis words in the block, but none were detected.",
    "error:27": "N line number value is not within the valid range of 1 – 9,999,999.",
    "error:28": "A G-code command was sent, but is missing some required P or L value words in the line.",
    "error:29": "Grbl supports six work coordinate systems G54-G59. G59.1, G59.2, and G59.3 are not supported.",
    "error:30": "The G53 G-code command requires either a G0 seek or G1 feed motion mode to be active. A different motion was active.",
    "error:31": "There are unused axis words in the block and G80 motion mode cancel is active.",
    "error:32": "A G2 or G3 arc was commanded but there are no XYZ axis words in the selected plane to trace the arc.",
    "error:33": "The motion command has an invalid target. G2, G3, and G38.2 generates this error, if the arc is impossible to generate or if the probe target is the current position.",
    "error:34": "A G2 or G3 arc, traced with the radius definition, had a mathematical error when computing the arc geometry. Try either breaking up the arc into semi-circles or quadrants, or redefine them with the arc offset definition.",
    "error:35": "A G2 or G3 arc, traced with the offset definition, is missing the IJK offset word in the selected plane to trace the arc.",
    "error:36": "There are unused, leftover G-code words that aren't used by any command in the block.",
    "error:37": "The G43.1 dynamic tool length offset command cannot apply an offset to an axis other than its configured axis. The Grbl default axis is the Z-axis.",
    "error:38": "An invalid tool number sent to the parser",
}


class InvertMask(Flag):
    INVERT_X = 1
    INVERT_Y = 1 << 1
    INVERT_Z = 1 << 2


class StatusReportMask(Flag):
    NOTHING = 0
    MACHINE_POSITION = 1
    WORK_POSITION = 1 << 1
    PLANNER_BUFFER = 1 << 2
    RX_BUFFER = 1 << 3
    LIMIT_PINS = 1 << 4


class GRBLSetting(Enum):
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
        return type(self._description[0])

    @property
    def default_value(self) -> float | bool | InvertMask | StatusReportMask | int:
        return self._description[0]

    @property
    def description(self) -> str:
        return self._description[1]

    @property
    def _description(self):
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
