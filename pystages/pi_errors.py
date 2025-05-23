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
# Copyright 2018-2024 Ledger SAS, written by Michaël Mouchous

from enum import Enum


class PIError(int, Enum):
    PI_CNTR_NO_ERROR = 0  # No error
    PI_CNTR_PARAM_SYNTAX = 1  # Parameter syntax error
    PI_CNTR_UNKNOWN_COMMAND = 2  # Unknown command
    PI_CNTR_COMMAND_TOO_LONG = (
        3  # Command length out of limits or command buffer overrun
    )
    PI_CNTR_SCAN_ERROR = 4  # Error while scanning
    PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO = 5  # Unallowable move attempted on unreferenced axis, or move attempted with servo off
    PI_CNTR_INVALID_SGA_PARAM = 6  # Parameter for SGA not valid
    PI_CNTR_POS_OUT_OF_LIMITS = 7  # Position out of limits
    PI_CNTR_VEL_OUT_OF_LIMITS = 8  # Velocity out of limits
    PI_CNTR_SET_PIVOT_NOT_POSSIBLE = (
        9  # Attempt to set pivot point while U,V and W not all 0
    )
    PI_CNTR_STOP = 10  # Controller was stopped by command
    PI_CNTR_SST_OR_SCAN_RANGE = (
        11  # Parameter for SST or for one of the embedded scan algorithms out of range
    )
    PI_CNTR_INVALID_SCAN_AXES = 12  # Invalid axis combination for fast scan
    PI_CNTR_INVALID_NAV_PARAM = 13  # Parameter for NAV out of range
    PI_CNTR_INVALID_ANALOG_INPUT = 14  # Invalid analog channel
    PI_CNTR_INVALID_AXIS_IDENTIFIER = 15  # Invalid axis identifier
    PI_CNTR_INVALID_STAGE_NAME = 16  # Unknown stage name
    PI_CNTR_PARAM_OUT_OF_RANGE = 17  # Parameter out of range
    PI_CNTR_INVALID_MACRO_NAME = 18  # Invalid macro name
    PI_CNTR_MACRO_RECORD = 19  # Error while recording macro
    PI_CNTR_MACRO_NOT_FOUND = 20  # Macro not found
    PI_CNTR_AXIS_HAS_NO_BRAKE = 21  # Axis has no brake
    PI_CNTR_DOUBLE_AXIS = 22  # Axis identifier specified more than once
    PI_CNTR_ILLEGAL_AXIS = 23  # Illegal axis
    PI_CNTR_PARAM_NR = 24  # Incorrect number of parameters
    PI_CNTR_INVALID_REAL_NR = 25  # Invalid floating point number
    PI_CNTR_MISSING_PARAM = 26  # Parameter missing
    PI_CNTR_SOFT_LIMIT_OUT_OF_RANGE = 27  # Soft limit out of range
    PI_CNTR_NO_MANUAL_PAD = 28  # No manual pad found
    PI_CNTR_NO_JUMP = 29  # No more step-response values
    PI_CNTR_INVALID_JUMP = 30  # No step-response values recorded
    PI_CNTR_AXIS_HAS_NO_REFERENCE = 31  # Axis has no reference sensor
    PI_CNTR_STAGE_HAS_NO_LIM_SWITCH = 32  # Axis has no limit switch
    PI_CNTR_NO_RELAY_CARD = 33  # No relay card installed
    PI_CNTR_CMD_NOT_ALLOWED_FOR_STAGE = 34  # Command not allowed for selected stage(s)
    PI_CNTR_NO_DIGITAL_INPUT = 35  # No digital input installed
    PI_CNTR_NO_DIGITAL_OUTPUT = 36  # No digital output configured
    PI_CNTR_NO_MCM = 37  # No more MCM responses
    PI_CNTR_INVALID_MCM = 38  # No MCM values recorded
    PI_CNTR_INVALID_CNTR_NUMBER = 39  # Controller number invalid
    PI_CNTR_NO_JOYSTICK_CONNECTED = 40  # No joystick configured
    PI_CNTR_INVALID_EGE_AXIS = (
        41  # Invalid axis for electronic gearing, axis can not be slave
    )
    PI_CNTR_SLAVE_POSITION_OUT_OF_RANGE = 42  # Position of slave axis is out of range
    PI_CNTR_COMMAND_EGE_SLAVE = (
        43  # Slave axis cannot be commanded directly when electronic gearing is enabled
    )
    PI_CNTR_JOYSTICK_CALIBRATION_FAILED = 44  # Calibration of joystick failed
    PI_CNTR_REFERENCING_FAILED = 45  # Referencing failed
    PI_CNTR_OPM_MISSING = 46  # OPM (Optical Power Meter) missing
    PI_CNTR_OPM_NOT_INITIALIZED = (
        47  # OPM (Optical Power Meter) not initialized or cannot be initialized
    )
    PI_CNTR_OPM_COM_ERROR = 48  # OPM (Optical Power Meter) Communication Error
    PI_CNTR_MOVE_TO_LIMIT_SWITCH_FAILED = 49  # Move to limit switch failed
    PI_CNTR_REF_WITH_REF_DISABLED = (
        50  # Attempt to reference axis with referencing disabled
    )
    PI_CNTR_AXIS_UNDER_JOYSTICK_CONTROL = 51  # Selected axis is controlled by joystick
    PI_CNTR_COMMUNICATION_ERROR = 52  # Controller detected communication error
    PI_CNTR_DYNAMIC_MOVE_IN_PROCESS = 53  # MOV! motion still in progress
    PI_CNTR_UNKNOWN_PARAMETER = 54  # Unknown parameter
    PI_CNTR_NO_REP_RECORDED = 55  # No commands were recorded with REP
    PI_CNTR_INVALID_PASSWORD = 56  # Password invalid
    PI_CNTR_INVALID_RECORDER_CHAN = 57  # Data Record Table does not exist
    PI_CNTR_INVALID_RECORDER_SRC_OPT = (
        58  # Source does not exist; number too low or too high
    )
    PI_CNTR_INVALID_RECORDER_SRC_CHAN = (
        59  # Source Record Table number too low or too high
    )
    PI_CNTR_PARAM_PROTECTION = (
        60  # Protected Param: current Command Level (CCL) too low
    )
    PI_CNTR_AUTOZERO_RUNNING = (
        61  # Command execution not possible while Autozero is running
    )
    PI_CNTR_NO_LINEAR_AXIS = 62  # Autozero requires at least one linear axis
    PI_CNTR_INIT_RUNNING = 63  # Initialization still in progress
    PI_CNTR_READ_ONLY_PARAMETER = 64  # Parameter is read-only
    PI_CNTR_PAM_NOT_FOUND = 65  # Parameter not found in non-volatile memory
    PI_CNTR_VOL_OUT_OF_LIMITS = 66  # Voltage out of limits
    PI_CNTR_WAVE_TOO_LARGE = 67  # Not enough memory available for requested wave curve
    PI_CNTR_NOT_ENOUGH_DDL_MEMORY = (
        68  # Not enough memory available for DDL table; DDL can not be started
    )
    PI_CNTR_DDL_TIME_DELAY_TOO_LARGE = (
        69  # Time delay larger than DDL table; DDL can not be started
    )
    PI_CNTR_DIFFERENT_ARRAY_LENGTH = (
        70  # The requested arrays have different lengths; query them separately
    )
    PI_CNTR_GEN_SINGLE_MODE_RESTART = (
        71  # Attempt to restart the generator while it is running in single step mode
    )
    PI_CNTR_ANALOG_TARGET_ACTIVE = 72  # Motion commands and wave generator activation are not allowed when analog target is active
    PI_CNTR_WAVE_GENERATOR_ACTIVE = (
        73  # Motion commands are not allowed when wave generator is active
    )
    PI_CNTR_AUTOZERO_DISABLED = 74  # No sensor channel or no piezo channel connected to selected axis (sensor andpiezo matrix)
    PI_CNTR_NO_WAVE_SELECTED = (
        75  # Generator started (WGO) without having selected a wave table (WSL).
    )
    PI_CNTR_IF_BUFFER_OVERRUN = (
        76  # Interface buffer did overrun and command couldn't be received correctly
    )
    PI_CNTR_NOT_ENOUGH_RECORDED_DATA = (
        77  # Data Record Table does not hold enough recorded data
    )
    PI_CNTR_TABLE_DEACTIVATED = 78  # Data Record Table is not configured for recording
    PI_CNTR_OPENLOOP_VALUE_SET_WHEN_SERVO_ON = (
        79  # Open-loop commands (SVA,SVR) are not allowed when servo is on
    )
    PI_CNTR_RAM_ERROR = 80  # Hardware error affecting RAM
    PI_CNTR_MACRO_UNKNOWN_COMMAND = 81  # Not macro command
    PI_CNTR_MACRO_PC_ERROR = 82  # Macro counter out of range
    PI_CNTR_JOYSTICK_ACTIVE = 83  # Joystick is active
    PI_CNTR_MOTOR_IS_OFF = 84  # Motor is off
    PI_CNTR_ONLY_IN_MACRO = 85  # Macro-only command
    PI_CNTR_JOYSTICK_UNKNOWN_AXIS = 86  # Invalid joystick axis
    PI_CNTR_JOYSTICK_UNKNOWN_ID = 87  # Joystick unknown
    PI_CNTR_REF_MODE_IS_ON = 88  # Move without referenced stage
    PI_CNTR_NOT_ALLOWED_IN_CURRENT_MOTION_MODE = (
        89  # Command not allowed in current motion mode
    )
    PI_CNTR_DIO_AND_TRACING_NOT_POSSIBLE = 90  # No tracing possible while digital IOs are used on this HW revision. Reconnect to switch operation mode.
    PI_CNTR_COLLISION = 91  # Move not possible, would cause collision
    PI_CNTR_SLAVE_NOT_FAST_ENOUGH = (
        92  # Stage is not capable of following the master. Check the gear ratio.
    )
    PI_CNTR_CMD_NOT_ALLOWED_WHILE_AXIS_IN_MOTION = 93  # This command is not allowed while the affected axis or its master is in motion.
    PI_CNTR_OPEN_LOOP_JOYSTICK_ENABLED = (
        94  # Servo cannot be switched on when open-loop joystick control is activated.
    )
    PI_CNTR_INVALID_SERVO_STATE_FOR_PARAMETER = (
        95  # This parameter cannot be changed in current servo mode.
    )
    PI_CNTR_UNKNOWN_STAGE_NAME = 96  # Unknown stage name
    PI_CNTR_INVALID_VALUE_LENGTH = 97  # Invalid length of value (too much characters)
    PI_CNTR_AUTOZERO_FAILED = 98  # AutoZero procedure was not successful
    PI_CNTR_SENSOR_VOLTAGE_OFF = 99  # Sensor voltage is off
    PI_LABVIEW_ERROR = 100  # PI driver for use with NILabVIEW reports error. See source control for details.
    PI_CNTR_NO_AXIS = 200  # No stage connected to axis
    PI_CNTR_NO_AXIS_PARAM_FILE = 201  # File with axis parameters not found
    PI_CNTR_INVALID_AXIS_PARAM_FILE = 202  # Invalid axis parameter file
    PI_CNTR_NO_AXIS_PARAM_BACKUP = 203  # Backup file with axis parameters not found
    PI_CNTR_RESERVED_204 = 204  # PI internal error code 204
    PI_CNTR_SMO_WITH_SERVO_ON = 205  # SMO with servo on
    PI_CNTR_UUDECODE_INCOMPLETE_HEADER = 206  # uudecode: incomplete header
    PI_CNTR_UUDECODE_NOTHING_TO_DECODE = 207  # uudecode: nothing to decode
    PI_CNTR_UUDECODE_ILLEGAL_FORMAT = 208  # uudecode: illegal UUE format
    PI_CNTR_CRC32_ERROR = 209  # CRC32 error
    PI_CNTR_ILLEGAL_FILENAME = 210  # Illegal file name (must be 8-0 format)
    PI_CNTR_FILE_NOT_FOUND = 211  # File not found on controller
    PI_CNTR_FILE_WRITE_ERROR = 212  # Error writing file on controller
    PI_CNTR_DTR_HINDERS_VELOCITY_CHANGE = (
        213  # VEL command not allowed in DTR Command Mode
    )
    PI_CNTR_POSITION_UNKNOWN = 214  # Position calculations failed
    PI_CNTR_CONN_POSSIBLY_BROKEN = (
        215  # The connection between controller and stage may be broken
    )
    PI_CNTR_ON_LIMIT_SWITCH = 216  # The connected stage has driven into a limit switch, some controllers need CLR to resume operation
    PI_CNTR_UNEXPECTED_STRUT_STOP = (
        217  # Strut test command failed because of an unexpected strut stop
    )
    PI_CNTR_POSITION_BASED_ON_ESTIMATION = (
        218  # While MOV! is running position can only beestimated!
    )
    PI_CNTR_POSITION_BASED_ON_INTERPOLATION = (
        219  # Position was calculated during MOV motion
    )
    PI_CNTR_INTERPOLATION_FIFO_UNDERRUN = (
        220  # FIFO buffer underrun during interpolation
    )
    PI_CNTR_INTERPOLATION_FIFO_OVERFLOW = (
        221  # FIFO buffer overflow during interpolation
    )
    PI_CNTR_INVALID_HANDLE = 230  # Invalid handle
    PI_CNTR_NO_BIOS_FOUND = 231  # No bios found
    PI_CNTR_SAVE_SYS_CFG_FAILED = 232  # Save system configuration failed
    PI_CNTR_LOAD_SYS_CFG_FAILED = 233  # Load system configuration failed
    PI_CNTR_SEND_BUFFER_OVERFLOW = 301  # Send buffer overflow
    PI_CNTR_VOLTAGE_OUT_OF_LIMITS = 302  # Voltage out of limits
    PI_CNTR_OPEN_LOOP_MOTION_SET_WHEN_SERVO_ON = (
        303  # Open-loop motion attempted when servo ON
    )
    PI_CNTR_RECEIVING_BUFFER_OVERFLOW = 304  # Received command is too long
    PI_CNTR_EEPROM_ERROR = 305  # Error while reading/writing EEPROM
    PI_CNTR_I2C_ERROR = 306  # Error on I2C bus
    PI_CNTR_RECEIVING_TIMEOUT = 307  # Timeout while receiving command
    PI_CNTR_TIMEOUT = 308  # A lengthy operation has not finished in the expected time
    PI_CNTR_MACRO_OUT_OF_SPACE = 309  # Insufficient space to store macro
    PI_CNTR_EUI_OLDVERSION_CFGDATA = 310  # Configuration data has old version number
    PI_CNTR_EUI_INVALID_CFGDATA = 311  # Invalid configuration data
    PI_CNTR_HARDWARE_ERROR = 333  # Internal hardware error
    PI_CNTR_WAV_INDEX_ERROR = 400  # Wave generator index error
    PI_CNTR_WAV_NOT_DEFINED = 401  # Wave table not defined
    PI_CNTR_WAV_TYPE_NOT_SUPPORTED = 402  # Wave type not supported
    PI_CNTR_WAV_LENGTH_EXCEEDS_LIMIT = 403  # Wave length exceeds limit
    PI_CNTR_WAV_PARAMETER_NR = 404  # Wave parameter number error
    PI_CNTR_WAV_PARAMETER_OUT_OF_LIMIT = 405  # Wave parameter out of range
    PI_CNTR_WGO_BIT_NOT_SUPPORTED = 406  # WGO command bit not supported
    PI_CNTR_EMERGENCY_STOP_BUTTON_ACTIVATED = (
        500  # The \"red knob\" is still set and disables system
    )
    PI_CNTR_EMERGENCY_STOP_BUTTON_WAS_ACTIVATED = 501  # The \"red knob\" was activated and still disables system - reanimation required
    PI_CNTR_REDUNDANCY_LIMIT_EXCEEDED = 502  # Position consistency check failed
    PI_CNTR_COLLISION_SWITCH_ACTIVATED = (
        503  # Hardware collision sensor(s) are activated
    )
    PI_CNTR_FOLLOWING_ERROR = 504  # Strut following error occurred, e.g. caused by overload or encoder failure
    PI_CNTR_SENSOR_SIGNAL_INVALID = 505  # One sensor signal is not valid
    PI_CNTR_SERVO_LOOP_UNSTABLE = 506  # Servo loop was unstable due to wrong parameter setting and switched off to avoid damage.
    PI_CNTR_LOST_SPI_SLAVE_CONNECTION = (
        507  # Digital connection to external SPI slave device is lost
    )
    PI_CNTR_MOVE_ATTEMPT_NOT_PERMITTED = (
        508  # Move attempt not permitted due to customer or limit settings
    )
    PI_CNTR_TRIGGER_EMERGENCY_STOP = 509  # Emergency stop caused by trigger input
    PI_CNTR_NODE_DOES_NOT_EXIST = 530  # A command refers to a node that does not exist
    PI_CNTR_PARENT_NODE_DOES_NOT_EXIST = (
        531  # A command refers to a node that has no parent node
    )
    PI_CNTR_NODE_IN_USE = 532  # Attempt to delete a node that is in use
    PI_CNTR_NODE_DEFINITION_IS_CYCLIC = 533  # Definition of a node is cyclic
    PI_CNTR_HEXAPOD_IN_MOTION = (
        536  # Transformation cannot be defined as long as Hexapod is in motion
    )
    PI_CNTR_TRANSFORMATION_TYPE_NOT_SUPPORTED = (
        537  # Transformation node cannot be activated
    )
    PI_CNTR_NODE_PARENT_IDENTICAL_TO_CHILD = 539  # A node cannot be linked to itself
    PI_CNTR_NODE_DEFINITION_INCONSISTE = 540  # NT
    PI_CNTR_NODES_NOT_IN_SAME_CHAIN = 542  # The nodes are not part of the Node definition is erroneous or not complete (replace or delete it) same chain
    PI_CNTR_NODE_MEMORY_FULL = (
        543  # Unused nodes must be deleted before new nodes can be stored
    )
    PI_CNTR_PIVOT_POINT_FEATURE_NOT_SUPPORTED = (
        544  # With some transformations pivot point usage is not supported
    )
    PI_CNTR_SOFTLIMITS_INVALID = (
        545  # Soft limits invalid due to changes in coordinate system
    )
    PI_CNTR_CS_WRITE_PROTECTED = 546  # Coordinate system is write protected
    PI_CNTR_CS_CONTENT_FROM_CONFIG_FILE = 547  # Coordinate system cannot be changed because its content is loaded from a configuration file
    PI_CNTR_CS_CANNOT_BE_LINKED = 548  # Coordinate system may not be linked
    PI_CNTR_KSB_CS_ROTATION_ONLY = 549  # A KSB-type coordinate system can only be rotated by multiples of 90 degrees
    PI_CNTR_CS_DATA_CANNOT_BE_QUERIED = (
        551  # This query is not supported for this coordinate system type
    )
    PI_CNTR_CS_COMBINATION_DOES_NOT_EXIST = (
        552  # This combination of work-and-tool coordinate system does not exist
    )
    PI_CNTR_CS_COMBINATION_INVALID = (
        553  # The combination must consist of one work and one tool coordinate system
    )
    PI_CNTR_CS_TYPE_DOES_NOT_EXIST = 554  # This coordinate system type does not exist
    PI_CNTR_UNKNOWN_ERROR = 555  # BasMac: unknown controller error
    PI_CNTR_CS_TYPE_NOT_ACTIVATED = (
        556  # No coordinate system of this type is activated
    )
    PI_CNTR_CS_NAME_INVALID = 557  # Name of coordinate system is invalid
    PI_CNTR_CS_GENERAL_FILE_MISSING = (
        558  # File with stored CS systems is missing or erroneous
    )
    PI_CNTR_CS_LEVELING_FILE_MISSING = (
        559  # File with leveling CS is missing or erroneous
    )
    PI_CNTR_NOT_ENOUGH_MEMORY = 601  # not enough memory
    PI_CNTR_HW_VOLTAGE_ERROR = 602  # hardware voltage error
    PI_CNTR_HW_TEMPERATURE_ERROR = 603  # hardware temperature out of range
    PI_CNTR_POSITION_ERROR_TOO_HIGH = (
        604  # Position error of any axis in the system is too high
    )
    PI_CNTR_INPUT_OUT_OF_RANGE = 606  # Maximum value of input signal has been exceeded
    PI_CNTR_NO_INTEGER = 607  # Value is not integer
    PI_CNTR_FAST_ALIGNMENT_PROCESS_IS_NOT_RUNNING = (
        608  # Fast alignment process cannot be paused because it is not running
    )
    PI_CNTR_FAST_ALIGNMENT_PROCESS_IS_NOT_PAUSED = 609  # Fast alignment process cannot be restarted/resumed because it is not paused
    PI_CNTR_UNABLE_TO_SET_PARAM_WITH_SPA = (
        650  # Parameter could not be set with SPA - SEP needed?
    )
    PI_CNTR_PHASE_FINDING_ERROR = 651  # Phase finding error
    PI_CNTR_SENSOR_SETUP_ERROR = 652  # Sensor setup error
    PI_CNTR_SENSOR_COMM_ERROR = 653  # Sensor communication error
    PI_CNTR_MOTOR_AMPLIFIER_ERROR = 654  # Motor amplifier error
    PI_CNTR_OVER_CURR_PROTEC_TRIGGERED_BY_I2T = (
        655  # Overcurrent protection triggered by I2T-module
    )
    PI_CNTR_OVER_CURR_PROTEC_TRIGGERED_BY_AMP_MODULE = (
        656  # Overcurrent protection triggered by amplifier module
    )
    PI_CNTR_SAFETY_STOP_TRIGGERED = 657  # Safety stop triggered
    PI_SENSOR_OFF = 658  # Sensor off?
    PI_CNTR_PARAM_CONFLICT = (
        659  # Parameter could not be set. Conflict with another parameter.
    )
    PI_CNTR_COMMAND_NOT_ALLOWED_IN_EXTERNAL_MODE = (
        700  # Command not allowed in external mode
    )
    PI_CNTR_EXTERNAL_MODE_ERROR = 710  # External mode communication error
    PI_CNTR_INVALID_MODE_OF_OPERATION = 715  # Invalid mode of operation
    PI_CNTR_FIRMWARE_STOPPED_BY_CMD = 716  # Firmware stopped by command (#27)
    PI_CNTR_EXTERNAL_MODE_DRIVER_MISSING = 717  # External mode driver missing
    PI_CNTR_CONFIGURATION_FAILURE_EXTERNAL_MODE = (
        718  # Missing or incorrect configuration of external mode
    )
    PI_CNTR_EXTERNAL_MODE_CYCLETIME_INVALID = 719  # External mode cycletime invalid
    PI_CNTR_BRAKE_ACTIVATED = 720  # Brake is activated
    PI_CNTR_DRIVE_STATE_TRANSITION_ERROR = 725  # Drive state transition error
    PI_CNTR_SURFACEDETECTION_RUNNING = (
        731  # Command not allowed while surface detection is running
    )
    PI_CNTR_SURFACEDETECTION_FAILED = 732  # Last surface detection failed
    PI_CNTR_FIELDBUS_IS_ACTIVE = (
        733  # Fieldbus is active and is blocking GCS control commands
    )
    PI_CNTR_TOO_MANY_NESTED_MACROS = 1000  # Too many nested macros
    PI_CNTR_MACRO_ALREADY_DEFINED = 1001  # Macro already defined
    PI_CNTR_NO_MACRO_RECORDING = 1002  # Macro recording not activated
    PI_CNTR_INVALID_MAC_PARAM = 1003  # Invalid parameter for MAC
    PI_CNTR_RESERVED_1004 = 1004  # PI internal error code 1004
    PI_CNTR_CONTROLLER_BUSY = 1005  # Controller is busy with some lengthy operation (e.g. reference move, fast scan algorithm)
    PI_CNTR_INVALID_IDENTIFIER = (
        1006  # Invalid identifier (invalid special characters, ...)
    )
    PI_CNTR_UNKNOWN_VARIABLE_OR_ARGUMENT = 1007  # Variable or argument not defined
    PI_CNTR_RUNNING_MACRO = 1008  # Controller is (already) running a macro
    PI_CNTR_MACRO_INVALID_OPERATOR = 1009  # Invalid or missing operator for condition. Check necessary spaces around operator.
    PI_CNTR_MACRO_NO_ANSWER = (
        1010  # No response was received while executing WAC/MEX/JRC/...
    )
    PI_CMD_NOT_VALID_IN_MACRO_MODE = 1011  # Command not valid during macro execution
    PI_CNTR_ERROR_IN_MACRO = 1012  # Error occured during macro execution
    PI_CNTR_NO_MACRO_OR_EMPTY = (
        1013  # No macro with given name on controller, or macro is empty
    )
    PI_CNTR_INVALID_ARGUMENT = 1015  # One or more arguments given to function is invalid (empty string, index out of range, ...)
    PI_CNTR_MOTION_ERROR = 1024  # Motion error: position error too large, servo is switched off automatically
    PI_CNTR_MAX_MOTOR_OUTPUT_REACHED = 1025  # Maximum motor output reached
    PI_CNTR_UNKNOWN_CHANNEL_IDENTIFIER = 1028  # Unknown channel identifier
    PI_CNTR_EXT_PROFILE_UNALLOWED_CMD = 1063  # User Profile Mode: Command is not allowed, check for required preparatory commands
    PI_CNTR_EXT_PROFILE_EXPECTING_MOTION_ERROR = 1064  # User Profile Mode: First target position in User Profile is too far from current position
    PI_CNTR_PROFILE_ACTIVE = 1065  # Controller is (already) in User Profile Mode
    PI_CNTR_PROFILE_INDEX_OUT_OF_RANGE = (
        1066  # User Profile Mode: Block or Data Set index out of allowed range
    )
    PI_CNTR_PROFILE_OUT_OF_MEMORY = 1071  # User Profile Mode: Out of memory
    PI_CNTR_PROFILE_WRONG_CLUSTER = (
        1072  # User Profile Mode: Cluster is not assigned to this axis
    )
    PI_CNTR_PROFILE_UNKNOWN_CLUSTER_IDENTIFIER = 1073  # Unknown cluster identifier
    PI_CNTR_TOO_MANY_TCP_CONNECTIONS_OPEN = (
        1090  # There are too many open tcpip connections
    )
    PI_CNTR_ALREADY_HAS_SERIAL_NUMBER = 2000  # Controller already has a serial number
    PI_CNTR_FEATURE_LICENSE_INVALID = 2100  # Entered license is invalid
    PI_CNTR_SECTOR_ERASE_FAILED = 4000  # Sector erase failed
    PI_CNTR_FLASH_PROGRAM_FAILED = 4001  # Flash program failed
    PI_CNTR_FLASH_READ_FAILED = 4002  # Flash read failed
    PI_CNTR_HW_MATCHCODE_ERROR = 4003  # HW match code missing/invalid
    PI_CNTR_FW_MATCHCODE_ERROR = 4004  # FW match code missing/invalid
    PI_CNTR_HW_VERSION_ERROR = 4005  # HW version missing/invalid
    PI_CNTR_FW_VERSION_ERROR = 4006  # FW version missing/invalid
    PI_CNTR_FW_UPDATE_ERROR = 4007  # FW update failed
    PI_CNTR_FW_CRC_PAR_ERROR = 4008  # FW Parameter CRC wrong
    PI_CNTR_FW_CRC_FW_ERROR = 4009  # FW CRC wrong
    PI_CNTR_INVALID_PCC_SCAN_DATA = 5000  # PicoCompensation scan data is not valid
    PI_CNTR_PCC_SCAN_RUNNING = 5001  # PicoCompensation is running, some actions can not be executed during scanning/recording
    PI_CNTR_INVALID_PCC_AXIS = 5002  # Given axis cannot be definedas PPC axis
    PI_CNTR_PCC_SCAN_OUT_OF_RANGE = (
        5003  # Defined scan area is larger than the travel range
    )
    PI_CNTR_PCC_TYPE_NOT_EXISTING = 5004  # Given PicoCompensation type is not defined
    PI_CNTR_PCC_PAM_ERROR = 5005  # PicoCompensation parameter error
    PI_CNTR_PCC_TABLE_ARRAY_TOO_LARGE = (
        5006  # PicoCompensation table is larger than maximum table length
    )
    PI_CNTR_NEXLINE_ERROR = 5100  # Common error in NEXLINE® firmware module
    PI_CNTR_CHANNEL_ALREADY_USED = (
        5101  # Output channel for NEXLINE® can not be redefined for other usage
    )
    PI_CNTR_NEXLINE_TABLE_TOO_SMALL = 5102  # Memory for NEXLINE® signals is too small
    PI_CNTR_RNP_WITH_SERVO_ON = (
        5103  # RNP can not be executed if axis is in closed loop
    )
    PI_CNTR_RNP_NEEDED = 5104  # Relax procedure (RNP) needed
    PI_CNTR_AXIS_NOT_CONFIGURED = 5200  # Axis must be configured for this action
    PI_CNTR_FREQU_ANALYSIS_FAILED = 5300  # Frequency analysis failed
    PI_CNTR_FREQU_ANALYSIS_RUNNING = 5301  # Another frequency analysis is running
    PI_CNTR_SENSOR_ABS_INVALID_VALUE = 6000  # Invalid preset value of absolute sensor
    PI_CNTR_SENSOR_ABS_WRITE_ERROR = 6001  # Error while writing to sensor
    PI_CNTR_SENSOR_ABS_READ_ERROR = 6002  # Error while reading from sensor
    PI_CNTR_SENSOR_ABS_CRC_ERROR = 6003  # Checksum error of absolute sensor
    PI_CNTR_SENSOR_ABS_ERROR = 6004  # General error of absolute sensor
    PI_CNTR_SENSOR_ABS_OVERFLOW = 6005  # Overflow of absolute sensor position
    COM_GPIB_ETAB = -28  # IEEE488: Return buffer full
    COM_GPIB_ELCK = -29  # IEEE488: Address or board locked
    COM_RS_INVALID_DATA_BITS = (
        -30
    )  # RS-232: 5 data bits with 2 stop bits is an invalid combination...
    COM_ERROR_RS_SETTINGS = -31  # RS-232: Error configuring the COM port
    COM_INTERNAL_RESOURCES_ERROR = (
        -32
    )  # Error dealing with internal system resources (events, threads, ...)
    COM_DLL_FUNC_ERROR = (
        -33
    )  # A DLL or one of the required functions could not be loaded
    COM_FTDIUSB_INVALID_HANDLE = -34  # FTDIUSB: invalid handle
    COM_FTDIUSB_DEVICE_NOT_FOUND = -35  # FTDIUSB: device not found
    COM_FTDIUSB_DEVICE_NOT_OPENED = -36  # FTDIUSB: device not opened
    COM_FTDIUSB_IO_ERROR = -37  # FTDIUSB: IO error
    COM_FTDIUSB_INSUFFICIENT_RESOURCES = -38  # FTDIUSB: insufficient resources
    COM_FTDIUSB_INVALID_PARAMETER = -39  # FTDIUSB: invalid parameter
    COM_FTDIUSB_INVALID_BAUD_RATE = -40  # FTDIUSB: invalid baud rate
    COM_FTDIUSB_DEVICE_NOT_OPENED_FOR_ERASE = (
        -41
    )  # FTDIUSB: device not opened for erase
    COM_FTDIUSB_DEVICE_NOT_OPENED_FOR_WRITE = (
        -42
    )  # FTDIUSB: device not opened for write
    COM_FTDIUSB_FAILED_TO_WRITE_DEVICE = -43  #  FTDIUSB: failed to write device
    COM_FTDIUSB_EEPROM_READ_FAILED = -44  # FTDIUSB: EEPROM read failed
    COM_FTDIUSB_EEPROM_WRITE_FAILED = -45  # FTDIUSB: EEPROM write failed
    COM_FTDIUSB_EEPROM_ERASE_FAILED = -46  # FTDIUSB: EEPROM erase failed
    COM_FTDIUSB_EEPROM_NOT_PRESENT = -47  # FTDIUSB: EEPROM not present
    COM_FTDIUSB_EEPROM_NOT_PROGRAMMED = -48  #  FTDIUSB: EEPROM not programmed
    COM_FTDIUSB_INVALID_ARGS = -49  # FTDIUSB: invalid arguments
    COM_FTDIUSB_NOT_SUPPORTED = -50  # FTDIUSB: not supported
    COM_FTDIUSB_OTHER_ERROR = -51  # FTDIUSB: other error
    COM_PORT_ALREADY_OPEN = -52  # Error while opening the COM port: was already open
    COM_PORT_CHECKSUM_ERROR = -53  # Checksum error in received data from COM port
    COM_SOCKET_NOT_READY = -54  # Socket not ready, you should call the function again
    COM_SOCKET_PORT_IN_USE = -55  # Port is used by another socket
    COM_SOCKET_NOT_CONNECTED = -56  # Socket not connected (or not valid)
    COM_SOCKET_TERMINATED = -57  # Connection terminated (by peer)
    COM_SOCKET_NO_RESPONSE = -58  # Can't connect to peer
    COM_SOCKET_INTERRUPTED = -59  # Operation was interrupted by a nonblocked signal
    COM_PCI_INVALID_ID = -60  # No device with this ID is present
    COM_PCI_ACCESS_DENIED = (
        -61
    )  # Driver could not be opened (on Vista: run as administrator!)
    COM_SOCKET_HOST_NOT_FOUND = -62  # Host not found
    COM_DEVICE_CONNECTED = -63  # Device already connected
    COM_INVALID_COM_PORT = -64  # Invalid COM port
    COM_USB_DEVICE_NOT_FOUND = -65  # USB device not found
    COM_NO_USB_DRIVER = -66  # No USB driver installed
    COM_USB_NOT_SUPPORTED = -67  # USB is not supported

    def __str__(self):
        return {
            self.PI_CNTR_NO_ERROR: "No error",
            self.PI_CNTR_PARAM_SYNTAX: "Parameter syntax error",
            self.PI_CNTR_UNKNOWN_COMMAND: "Unknown command",
            self.PI_CNTR_COMMAND_TOO_LONG: "Command length out of limits or command buffer overrun",
            self.PI_CNTR_SCAN_ERROR: "Error while scanning",
            self.PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO: "Unallowable move attempted on unreferenced axis, or move attempted with servo off",
            self.PI_CNTR_INVALID_SGA_PARAM: "Parameter for SGA not valid",
            self.PI_CNTR_POS_OUT_OF_LIMITS: "Position out of limits",
            self.PI_CNTR_VEL_OUT_OF_LIMITS: "Velocity out of limits",
            self.PI_CNTR_SET_PIVOT_NOT_POSSIBLE: "Attempt to set pivot point while U,V and W not all 0",
            self.PI_CNTR_STOP: "Controller was stopped by command",
            self.PI_CNTR_SST_OR_SCAN_RANGE: "Parameter for SST or for one of the embedded scan algorithms out of range",
            self.PI_CNTR_INVALID_SCAN_AXES: "Invalid axis combination for fast scan",
            self.PI_CNTR_INVALID_NAV_PARAM: "Parameter for NAV out of range",
            self.PI_CNTR_INVALID_ANALOG_INPUT: "Invalid analog channel",
            self.PI_CNTR_INVALID_AXIS_IDENTIFIER: "Invalid axis identifier",
            self.PI_CNTR_INVALID_STAGE_NAME: "Unknown stage name",
            self.PI_CNTR_PARAM_OUT_OF_RANGE: "Parameter out of range",
            self.PI_CNTR_INVALID_MACRO_NAME: "Invalid macro name",
            self.PI_CNTR_MACRO_RECORD: "Error while recording macro",
            self.PI_CNTR_MACRO_NOT_FOUND: "Macro not found",
            self.PI_CNTR_AXIS_HAS_NO_BRAKE: "Axis has no brake",
            self.PI_CNTR_DOUBLE_AXIS: "Axis identifier specified more than once",
            self.PI_CNTR_ILLEGAL_AXIS: "Illegal axis",
            self.PI_CNTR_PARAM_NR: "Incorrect number of parameters",
            self.PI_CNTR_INVALID_REAL_NR: "Invalid floating point number",
            self.PI_CNTR_MISSING_PARAM: "Parameter missing",
            self.PI_CNTR_SOFT_LIMIT_OUT_OF_RANGE: "Soft limit out of range",
            self.PI_CNTR_NO_MANUAL_PAD: "No manual pad found",
            self.PI_CNTR_NO_JUMP: "No more step-response values",
            self.PI_CNTR_INVALID_JUMP: "No step-response values recorded",
            self.PI_CNTR_AXIS_HAS_NO_REFERENCE: "Axis has no reference sensor",
            self.PI_CNTR_STAGE_HAS_NO_LIM_SWITCH: "Axis has no limit switch",
            self.PI_CNTR_NO_RELAY_CARD: "No relay card installed",
            self.PI_CNTR_CMD_NOT_ALLOWED_FOR_STAGE: "Command not allowed for selected stage(s)",
            self.PI_CNTR_NO_DIGITAL_INPUT: "No digital input installed",
            self.PI_CNTR_NO_DIGITAL_OUTPUT: "No digital output configured",
            self.PI_CNTR_NO_MCM: "No more MCM responses",
            self.PI_CNTR_INVALID_MCM: "No MCM values recorded",
            self.PI_CNTR_INVALID_CNTR_NUMBER: "Controller number invalid",
            self.PI_CNTR_NO_JOYSTICK_CONNECTED: "No joystick configured",
            self.PI_CNTR_INVALID_EGE_AXIS: "Invalid axis for electronic gearing, axis can not be slave",
            self.PI_CNTR_SLAVE_POSITION_OUT_OF_RANGE: "Position of slave axis is out of range",
            self.PI_CNTR_COMMAND_EGE_SLAVE: "Slave axis cannot be commanded directly when electronic gearing is enabled",
            self.PI_CNTR_JOYSTICK_CALIBRATION_FAILED: "Calibration of joystick failed",
            self.PI_CNTR_REFERENCING_FAILED: "Referencing failed",
            self.PI_CNTR_OPM_MISSING: "OPM (Optical Power Meter) missing",
            self.PI_CNTR_OPM_NOT_INITIALIZED: "OPM (Optical Power Meter) not initialized or cannot be initialized",
            self.PI_CNTR_OPM_COM_ERROR: "OPM (Optical Power Meter) Communication Error ",
            self.PI_CNTR_MOVE_TO_LIMIT_SWITCH_FAILED: "Move to limit switch failed",
            self.PI_CNTR_REF_WITH_REF_DISABLED: "Attempt to reference axis with referencing disabled",
            self.PI_CNTR_AXIS_UNDER_JOYSTICK_CONTROL: "Selected axis is controlled by joystick",
            self.PI_CNTR_COMMUNICATION_ERROR: "Controller detected communication error",
            self.PI_CNTR_DYNAMIC_MOVE_IN_PROCESS: "MOV! motion still in progress",
            self.PI_CNTR_UNKNOWN_PARAMETER: "Unknown parameter",
            self.PI_CNTR_NO_REP_RECORDED: "No commands were recorded with REP",
            self.PI_CNTR_INVALID_PASSWORD: "Password invalid",
            self.PI_CNTR_INVALID_RECORDER_CHAN: "Data Record Table does not exist",
            self.PI_CNTR_INVALID_RECORDER_SRC_OPT: "Source does not exist; number too low or too high",
            self.PI_CNTR_INVALID_RECORDER_SRC_CHAN: "Source Record Table number too low or too high",
            self.PI_CNTR_PARAM_PROTECTION: "Protected Param: current Command Level (CCL) too low",
            self.PI_CNTR_AUTOZERO_RUNNING: "Command execution not possible while Autozero is running",
            self.PI_CNTR_NO_LINEAR_AXIS: "Autozero requires at least one linear axis",
            self.PI_CNTR_INIT_RUNNING: "Initialization still in progress",
            self.PI_CNTR_READ_ONLY_PARAMETER: "Parameter is read-only",
            self.PI_CNTR_PAM_NOT_FOUND: "Parameter not found in non-volatile memory",
            self.PI_CNTR_VOL_OUT_OF_LIMITS: "Voltage out of limits",
            self.PI_CNTR_WAVE_TOO_LARGE: "Not enough memory available for requested wave curve",
            self.PI_CNTR_NOT_ENOUGH_DDL_MEMORY: "Not enough memory available for DDL table; DDL can not be started",
            self.PI_CNTR_DDL_TIME_DELAY_TOO_LARGE: "Time delay larger than DDL table; DDL can not be started",
            self.PI_CNTR_DIFFERENT_ARRAY_LENGTH: "The requested arrays have different lengths; query them separately",
            self.PI_CNTR_GEN_SINGLE_MODE_RESTART: "Attempt to restart the generator while it is running in single step mode",
            self.PI_CNTR_ANALOG_TARGET_ACTIVE: "Motion commands and wave generator activation are not allowed when analog target is active",
            self.PI_CNTR_WAVE_GENERATOR_ACTIVE: "Motion commands are not allowed when wave generator is active",
            self.PI_CNTR_AUTOZERO_DISABLED: "No sensor channel or no piezo channel connected to selected axis (sensor andpiezo matrix)",
            self.PI_CNTR_NO_WAVE_SELECTED: "Generator started (WGO) without having selected a wave table (WSL).",
            self.PI_CNTR_IF_BUFFER_OVERRUN: "Interface buffer did overrun and command couldn't be received correctly",
            self.PI_CNTR_NOT_ENOUGH_RECORDED_DATA: "Data Record Table does not hold enough recorded data",
            self.PI_CNTR_TABLE_DEACTIVATED: "Data Record Table is not configured for recording",
            self.PI_CNTR_OPENLOOP_VALUE_SET_WHEN_SERVO_ON: "Open-loop commands (SVA,SVR) are not allowed when servo is on",
            self.PI_CNTR_RAM_ERROR: "Hardware error affecting RAM",
            self.PI_CNTR_MACRO_UNKNOWN_COMMAND: "Not macro command",
            self.PI_CNTR_MACRO_PC_ERROR: "Macro counter out of range",
            self.PI_CNTR_JOYSTICK_ACTIVE: "Joystick is active",
            self.PI_CNTR_MOTOR_IS_OFF: "Motor is off",
            self.PI_CNTR_ONLY_IN_MACRO: "Macro-only command",
            self.PI_CNTR_JOYSTICK_UNKNOWN_AXIS: "Invalid joystick axis",
            self.PI_CNTR_JOYSTICK_UNKNOWN_ID: "Joystick unknown",
            self.PI_CNTR_REF_MODE_IS_ON: "Move without referenced stage",
            self.PI_CNTR_NOT_ALLOWED_IN_CURRENT_MOTION_MODE: "Command not allowed in current motion mode",
            self.PI_CNTR_DIO_AND_TRACING_NOT_POSSIBLE: "No tracing possible while digital IOs are used on this HW revision. Reconnect to switch operation mode.",
            self.PI_CNTR_COLLISION: "Move not possible, would cause collision",
            self.PI_CNTR_SLAVE_NOT_FAST_ENOUGH: "Stage is not capable of following the master. Check the gear ratio.",
            self.PI_CNTR_CMD_NOT_ALLOWED_WHILE_AXIS_IN_MOTION: "This command is not allowed while the affected axis or its master is in motion.",
            self.PI_CNTR_OPEN_LOOP_JOYSTICK_ENABLED: "Servo cannot be switched on when open-loop joystick control is activated.",
            self.PI_CNTR_INVALID_SERVO_STATE_FOR_PARAMETER: "This parameter cannot be changed in current servo mode.",
            self.PI_CNTR_UNKNOWN_STAGE_NAME: "Unknown stage name",
            self.PI_CNTR_INVALID_VALUE_LENGTH: "Invalid length of value (too much characters)",
            self.PI_CNTR_AUTOZERO_FAILED: "AutoZero procedure was not successful",
            self.PI_CNTR_SENSOR_VOLTAGE_OFF: "Sensor voltage is off",
            self.PI_LABVIEW_ERROR: "PI driver for use with NILabVIEW reports error. See source control for details.",
            self.PI_CNTR_NO_AXIS: "No stage connected to axis",
            self.PI_CNTR_NO_AXIS_PARAM_FILE: "File with axis parameters not found",
            self.PI_CNTR_INVALID_AXIS_PARAM_FILE: "Invalid axis parameter file",
            self.PI_CNTR_NO_AXIS_PARAM_BACKUP: "Backup file with axis parameters not found",
            self.PI_CNTR_RESERVED_204: "PI internal error code 204",
            self.PI_CNTR_SMO_WITH_SERVO_ON: "SMO with servo on",
            self.PI_CNTR_UUDECODE_INCOMPLETE_HEADER: "uudecode: incomplete header ",
            self.PI_CNTR_UUDECODE_NOTHING_TO_DECODE: "uudecode: nothing to decode",
            self.PI_CNTR_UUDECODE_ILLEGAL_FORMAT: "uudecode: illegal UUE format",
            self.PI_CNTR_CRC32_ERROR: "CRC32 error",
            self.PI_CNTR_ILLEGAL_FILENAME: "Illegal file name (must be 8-0 format)",
            self.PI_CNTR_FILE_NOT_FOUND: "File not found on controller",
            self.PI_CNTR_FILE_WRITE_ERROR: "Error writing file on controller",
            self.PI_CNTR_DTR_HINDERS_VELOCITY_CHANGE: "VEL command not allowed in DTR Command Mode",
            self.PI_CNTR_POSITION_UNKNOWN: "Position calculations failed",
            self.PI_CNTR_CONN_POSSIBLY_BROKEN: "The connection between controller and stage may be broken",
            self.PI_CNTR_ON_LIMIT_SWITCH: "The connected stage has driven into a limit switch, some controllers need CLR to resume operation",
            self.PI_CNTR_UNEXPECTED_STRUT_STOP: "Strut test command failed because of an unexpected strut stop",
            self.PI_CNTR_POSITION_BASED_ON_ESTIMATION: "While MOV! is running position can only beestimated!",
            self.PI_CNTR_POSITION_BASED_ON_INTERPOLATION: "Position was calculated during MOV motion",
            self.PI_CNTR_INTERPOLATION_FIFO_UNDERRUN: "FIFO buffer underrun during interpolation",
            self.PI_CNTR_INTERPOLATION_FIFO_OVERFLOW: "FIFO buffer overflow during interpolation",
            self.PI_CNTR_INVALID_HANDLE: "Invalid handle",
            self.PI_CNTR_NO_BIOS_FOUND: "No bios found",
            self.PI_CNTR_SAVE_SYS_CFG_FAILED: "Save system configuration failed",
            self.PI_CNTR_LOAD_SYS_CFG_FAILED: "Load system configuration failed",
            self.PI_CNTR_SEND_BUFFER_OVERFLOW: "Send buffer overflow",
            self.PI_CNTR_VOLTAGE_OUT_OF_LIMITS: "Voltage out of limits",
            self.PI_CNTR_OPEN_LOOP_MOTION_SET_WHEN_SERVO_ON: "Open-loop motion attempted when servo ON",
            self.PI_CNTR_RECEIVING_BUFFER_OVERFLOW: "Received command is too long",
            self.PI_CNTR_EEPROM_ERROR: "Error while reading/writing EEPROM",
            self.PI_CNTR_I2C_ERROR: "Error on I2C bus",
            self.PI_CNTR_RECEIVING_TIMEOUT: "Timeout while receiving command",
            self.PI_CNTR_TIMEOUT: "A lengthy operation has not finished in the expected time",
            self.PI_CNTR_MACRO_OUT_OF_SPACE: "Insufficient space to store macro",
            self.PI_CNTR_EUI_OLDVERSION_CFGDATA: "Configuration data has old version number",
            self.PI_CNTR_EUI_INVALID_CFGDATA: "Invalid configuration data",
            self.PI_CNTR_HARDWARE_ERROR: "Internal hardware error",
            self.PI_CNTR_WAV_INDEX_ERROR: "Wave generator index error",
            self.PI_CNTR_WAV_NOT_DEFINED: "Wave table not defined",
            self.PI_CNTR_WAV_TYPE_NOT_SUPPORTED: "Wave type not supported",
            self.PI_CNTR_WAV_LENGTH_EXCEEDS_LIMIT: "Wave length exceeds limit",
            self.PI_CNTR_WAV_PARAMETER_NR: "Wave parameter number error",
            self.PI_CNTR_WAV_PARAMETER_OUT_OF_LIMIT: "Wave parameter out of range",
            self.PI_CNTR_WGO_BIT_NOT_SUPPORTED: "WGO command bit not supported",
            self.PI_CNTR_EMERGENCY_STOP_BUTTON_ACTIVATED: 'The "red knob" is still set and disables system',
            self.PI_CNTR_EMERGENCY_STOP_BUTTON_WAS_ACTIVATED: 'The "red knob" was activated and still disables system - reanimation required',
            self.PI_CNTR_REDUNDANCY_LIMIT_EXCEEDED: "Position consistency check failed",
            self.PI_CNTR_COLLISION_SWITCH_ACTIVATED: "Hardware collision sensor(s) are activated",
            self.PI_CNTR_FOLLOWING_ERROR: "Strut following error occurred, e.g. caused by overload or encoder failure",
            self.PI_CNTR_SENSOR_SIGNAL_INVALID: "One sensor signal is not valid",
            self.PI_CNTR_SERVO_LOOP_UNSTABLE: "Servo loop was unstable due to wrong parameter setting and switched off to avoid damage.",
            self.PI_CNTR_LOST_SPI_SLAVE_CONNECTION: "Digital connection to external SPI slave device is lost",
            self.PI_CNTR_MOVE_ATTEMPT_NOT_PERMITTED: "Move attempt not permitted due to customer or limit settings",
            self.PI_CNTR_TRIGGER_EMERGENCY_STOP: "Emergency stop caused by trigger input",
            self.PI_CNTR_NODE_DOES_NOT_EXIST: "A command refers to a node that does not exist",
            self.PI_CNTR_PARENT_NODE_DOES_NOT_EXIST: "A command refers to a node that has no parent node",
            self.PI_CNTR_NODE_IN_USE: "Attempt to delete a node that is in use",
            self.PI_CNTR_NODE_DEFINITION_IS_CYCLIC: "Definition of a node is cyclic",
            self.PI_CNTR_HEXAPOD_IN_MOTION: "Transformation cannot be defined as long as Hexapod is in motion",
            self.PI_CNTR_TRANSFORMATION_TYPE_NOT_SUPPORTED: "Transformation node cannot be activated",
            self.PI_CNTR_NODE_PARENT_IDENTICAL_TO_CHILD: "A node cannot be linked to itself",
            self.PI_CNTR_NODE_DEFINITION_INCONSISTE: "NT",
            self.PI_CNTR_NODES_NOT_IN_SAME_CHAIN: "The nodes are not part of the Node definition is erroneous or not complete (replace or delete it) same chain",
            self.PI_CNTR_NODE_MEMORY_FULL: "Unused nodes must be deleted before new nodes can be stored",
            self.PI_CNTR_PIVOT_POINT_FEATURE_NOT_SUPPORTED: "With some transformations pivot point usage is not supported",
            self.PI_CNTR_SOFTLIMITS_INVALID: "Soft limits invalid due to changes in coordinate system ",
            self.PI_CNTR_CS_WRITE_PROTECTED: "Coordinate system is write protected",
            self.PI_CNTR_CS_CONTENT_FROM_CONFIG_FILE: "Coordinate system cannot be changed because its content is loaded from a configuration file",
            self.PI_CNTR_CS_CANNOT_BE_LINKED: "Coordinate system may not be linked",
            self.PI_CNTR_KSB_CS_ROTATION_ONLY: "A KSB-type coordinate system can only be rotated by multiples of 90 degrees",
            self.PI_CNTR_CS_DATA_CANNOT_BE_QUERIED: "This query is not supported for this coordinate system type",
            self.PI_CNTR_CS_COMBINATION_DOES_NOT_EXIST: "This combination of work-and-tool coordinate system does not exist",
            self.PI_CNTR_CS_COMBINATION_INVALID: "The combination must consist of one work and one tool coordinate system",
            self.PI_CNTR_CS_TYPE_DOES_NOT_EXIST: "This coordinate system type does not exist",
            self.PI_CNTR_UNKNOWN_ERROR: "BasMac: unknown controller error",
            self.PI_CNTR_CS_TYPE_NOT_ACTIVATED: "No coordinate system of this type is activated",
            self.PI_CNTR_CS_NAME_INVALID: "Name of coordinate system is invalid",
            self.PI_CNTR_CS_GENERAL_FILE_MISSING: "File with stored CS systems is missing or erroneous",
            self.PI_CNTR_CS_LEVELING_FILE_MISSING: "File with leveling CS is missing or erroneous",
            self.PI_CNTR_NOT_ENOUGH_MEMORY: "not enough memory",
            self.PI_CNTR_HW_VOLTAGE_ERROR: "hardware voltage error",
            self.PI_CNTR_HW_TEMPERATURE_ERROR: "hardware temperature out of range",
            self.PI_CNTR_POSITION_ERROR_TOO_HIGH: "Position error of any axis in the system is too high",
            self.PI_CNTR_INPUT_OUT_OF_RANGE: "Maximum value of input signal has been exceeded",
            self.PI_CNTR_NO_INTEGER: "Value is not integer",
            self.PI_CNTR_FAST_ALIGNMENT_PROCESS_IS_NOT_RUNNING: "Fast alignment process cannot be paused because it is not running",
            self.PI_CNTR_FAST_ALIGNMENT_PROCESS_IS_NOT_PAUSED: "Fast alignment process cannot be restarted/resumed because it is not paused",
            self.PI_CNTR_UNABLE_TO_SET_PARAM_WITH_SPA: "Parameter could not be set with SPA - SEP needed?",
            self.PI_CNTR_PHASE_FINDING_ERROR: "Phase finding error",
            self.PI_CNTR_SENSOR_SETUP_ERROR: "Sensor setup error",
            self.PI_CNTR_SENSOR_COMM_ERROR: "Sensor communication error",
            self.PI_CNTR_MOTOR_AMPLIFIER_ERROR: "Motor amplifier error",
            self.PI_CNTR_OVER_CURR_PROTEC_TRIGGERED_BY_I2T: "Overcurrent protection triggered by I2T-module",
            self.PI_CNTR_OVER_CURR_PROTEC_TRIGGERED_BY_AMP_MODULE: "Overcurrent protection triggered by amplifier module",
            self.PI_CNTR_SAFETY_STOP_TRIGGERED: "Safety stop triggered",
            self.PI_SENSOR_OFF: "Sensor off?",
            self.PI_CNTR_PARAM_CONFLICT: "Parameter could not be set. Conflict with another parameter.",
            self.PI_CNTR_COMMAND_NOT_ALLOWED_IN_EXTERNAL_MODE: "Command not allowed in external mode",
            self.PI_CNTR_EXTERNAL_MODE_ERROR: "External mode communication error",
            self.PI_CNTR_INVALID_MODE_OF_OPERATION: "Invalid mode of operation",
            self.PI_CNTR_FIRMWARE_STOPPED_BY_CMD: "Firmware stopped by command (#27)",
            self.PI_CNTR_EXTERNAL_MODE_DRIVER_MISSING: "External mode driver missing",
            self.PI_CNTR_CONFIGURATION_FAILURE_EXTERNAL_MODE: "Missing or incorrect configuration of external mode",
            self.PI_CNTR_EXTERNAL_MODE_CYCLETIME_INVALID: "External mode cycletime invalid",
            self.PI_CNTR_BRAKE_ACTIVATED: "Brake is activated",
            self.PI_CNTR_DRIVE_STATE_TRANSITION_ERROR: "Drive state transition error",
            self.PI_CNTR_SURFACEDETECTION_RUNNING: "Command not allowed while surface detection is running",
            self.PI_CNTR_SURFACEDETECTION_FAILED: "Last surface detection failed",
            self.PI_CNTR_FIELDBUS_IS_ACTIVE: "Fieldbus is active and is blocking GCS control commands",
            self.PI_CNTR_TOO_MANY_NESTED_MACROS: "Too many nested macros",
            self.PI_CNTR_MACRO_ALREADY_DEFINED: "Macro already defined",
            self.PI_CNTR_NO_MACRO_RECORDING: "Macro recording not activated",
            self.PI_CNTR_INVALID_MAC_PARAM: "Invalid parameter for MAC",
            self.PI_CNTR_RESERVED_1004: "PI internal error code 1004",
            self.PI_CNTR_CONTROLLER_BUSY: "Controller is busy with some lengthy operation (e.g. reference move, fast scan algorithm)",
            self.PI_CNTR_INVALID_IDENTIFIER: "Invalid identifier (invalid special characters, ...)",
            self.PI_CNTR_UNKNOWN_VARIABLE_OR_ARGUMENT: "Variable or argument not defined",
            self.PI_CNTR_RUNNING_MACRO: "Controller is (already) running a macro",
            self.PI_CNTR_MACRO_INVALID_OPERATOR: "Invalid or missing operator for condition. Check necessary spaces around operator.",
            self.PI_CNTR_MACRO_NO_ANSWER: "No response was received while executing WAC/MEX/JRC/...",
            self.PI_CMD_NOT_VALID_IN_MACRO_MODE: "Command not valid during macro execution",
            self.PI_CNTR_ERROR_IN_MACRO: "Error occured during macro execution",
            self.PI_CNTR_NO_MACRO_OR_EMPTY: "No macro with given name on controller, or macro is empty",
            self.PI_CNTR_INVALID_ARGUMENT: "One or more arguments given to function is invalid (empty string, index out of range, ...)",
            self.PI_CNTR_MOTION_ERROR: "Motion error: position error too large, servo is switched off automatically ",
            self.PI_CNTR_MAX_MOTOR_OUTPUT_REACHED: "Maximum motor output reached",
            self.PI_CNTR_UNKNOWN_CHANNEL_IDENTIFIER: "Unknown channel identifier",
            self.PI_CNTR_EXT_PROFILE_UNALLOWED_CMD: "User Profile Mode: Command is not allowed, check for required preparatory commands",
            self.PI_CNTR_EXT_PROFILE_EXPECTING_MOTION_ERROR: "User Profile Mode: First target position in User Profile is too far from current position",
            self.PI_CNTR_PROFILE_ACTIVE: "Controller is (already) in User Profile Mode",
            self.PI_CNTR_PROFILE_INDEX_OUT_OF_RANGE: "User Profile Mode: Block or Data Set index out of allowed range ",
            self.PI_CNTR_PROFILE_OUT_OF_MEMORY: "User Profile Mode: Out of memory",
            self.PI_CNTR_PROFILE_WRONG_CLUSTER: "User Profile Mode: Cluster is not assigned to this axis",
            self.PI_CNTR_PROFILE_UNKNOWN_CLUSTER_IDENTIFIER: "Unknown cluster identifier",
            self.PI_CNTR_TOO_MANY_TCP_CONNECTIONS_OPEN: "There are too many open tcpip connections",
            self.PI_CNTR_ALREADY_HAS_SERIAL_NUMBER: "Controller already has a serial number",
            self.PI_CNTR_FEATURE_LICENSE_INVALID: "Entered license is invalid",
            self.PI_CNTR_SECTOR_ERASE_FAILED: "Sector erase failed",
            self.PI_CNTR_FLASH_PROGRAM_FAILED: "Flash program failed",
            self.PI_CNTR_FLASH_READ_FAILED: "Flash read failed",
            self.PI_CNTR_HW_MATCHCODE_ERROR: "HW match code missing/invalid",
            self.PI_CNTR_FW_MATCHCODE_ERROR: "FW match code missing/invalid",
            self.PI_CNTR_HW_VERSION_ERROR: "HW version missing/invalid",
            self.PI_CNTR_FW_VERSION_ERROR: "FW version missing/invalid",
            self.PI_CNTR_FW_UPDATE_ERROR: "FW update failed",
            self.PI_CNTR_FW_CRC_PAR_ERROR: "FW Parameter CRC wrong",
            self.PI_CNTR_FW_CRC_FW_ERROR: "FW CRC wrong",
            self.PI_CNTR_INVALID_PCC_SCAN_DATA: "PicoCompensation scan data is not valid",
            self.PI_CNTR_PCC_SCAN_RUNNING: "PicoCompensation is running, some actions can not be executed during scanning/recording",
            self.PI_CNTR_INVALID_PCC_AXIS: "Given axis cannot be definedas PPC axis",
            self.PI_CNTR_PCC_SCAN_OUT_OF_RANGE: "Defined scan area is larger than the travel range",
            self.PI_CNTR_PCC_TYPE_NOT_EXISTING: "Given PicoCompensation type is not defined",
            self.PI_CNTR_PCC_PAM_ERROR: "PicoCompensation parameter error",
            self.PI_CNTR_PCC_TABLE_ARRAY_TOO_LARGE: "PicoCompensation table is larger than maximum table length",
            self.PI_CNTR_NEXLINE_ERROR: "Common error in NEXLINE® firmware module",
            self.PI_CNTR_CHANNEL_ALREADY_USED: "Output channel for NEXLINE® can not be redefined for other usage",
            self.PI_CNTR_NEXLINE_TABLE_TOO_SMALL: "Memory for NEXLINE® signals is too small",
            self.PI_CNTR_RNP_WITH_SERVO_ON: "RNP can not be executed if axis is in closed loop",
            self.PI_CNTR_RNP_NEEDED: "Relax procedure (RNP) needed",
            self.PI_CNTR_AXIS_NOT_CONFIGURED: "Axis must be configured for this action",
            self.PI_CNTR_FREQU_ANALYSIS_FAILED: "Frequency analysis failed",
            self.PI_CNTR_FREQU_ANALYSIS_RUNNING: "Another frequency analysis is running",
            self.PI_CNTR_SENSOR_ABS_INVALID_VALUE: "Invalid preset value of absolute sensor",
            self.PI_CNTR_SENSOR_ABS_WRITE_ERROR: "Error while writing to sensor",
            self.PI_CNTR_SENSOR_ABS_READ_ERROR: "Error while reading from sensor",
            self.PI_CNTR_SENSOR_ABS_CRC_ERROR: "Checksum error of absolute sensor",
            self.PI_CNTR_SENSOR_ABS_ERROR: "General error of absolute sensor",
            self.PI_CNTR_SENSOR_ABS_OVERFLOW: "Overflow of absolute sensor position",
            self.COM_GPIB_ETAB: "IEEE488: Return buffer full",
            self.COM_GPIB_ELCK: "IEEE488: Address or board locked",
            self.COM_RS_INVALID_DATA_BITS: "RS-232: 5 data bits with 2 stop bits is an invalid combination, as is 6, 7, or 8 data bits with 1.5 stop bits",
            self.COM_ERROR_RS_SETTINGS: "RS-232: Error configuring the COM port",
            self.COM_INTERNAL_RESOURCES_ERROR: "Error dealing with internal system resources (events, threads, ...)",
            self.COM_DLL_FUNC_ERROR: "A DLL or one of the required functions could not be loaded",
            self.COM_FTDIUSB_INVALID_HANDLE: "FTDIUSB: invalid handle",
            self.COM_FTDIUSB_DEVICE_NOT_FOUND: "FTDIUSB: device not found",
            self.COM_FTDIUSB_DEVICE_NOT_OPENED: "FTDIUSB: device not opened",
            self.COM_FTDIUSB_IO_ERROR: "FTDIUSB: IO error",
            self.COM_FTDIUSB_INSUFFICIENT_RESOURCES: "FTDIUSB: insufficient resources",
            self.COM_FTDIUSB_INVALID_PARAMETER: "FTDIUSB: invalid parameter",
            self.COM_FTDIUSB_INVALID_BAUD_RATE: "FTDIUSB: invalid baud rate",
            self.COM_FTDIUSB_DEVICE_NOT_OPENED_FOR_ERASE: "FTDIUSB: device not opened for erase",
            self.COM_FTDIUSB_DEVICE_NOT_OPENED_FOR_WRITE: "FTDIUSB: device not opened for write ",
            self.COM_FTDIUSB_FAILED_TO_WRITE_DEVICE: " FTDIUSB: failed to write device",
            self.COM_FTDIUSB_EEPROM_READ_FAILED: "FTDIUSB: EEPROM read failed",
            self.COM_FTDIUSB_EEPROM_WRITE_FAILED: "FTDIUSB: EEPROM write failed",
            self.COM_FTDIUSB_EEPROM_ERASE_FAILED: "FTDIUSB: EEPROM erase failed",
            self.COM_FTDIUSB_EEPROM_NOT_PRESENT: "FTDIUSB: EEPROM not present",
            self.COM_FTDIUSB_EEPROM_NOT_PROGRAMMED: " FTDIUSB: EEPROM not programmed",
            self.COM_FTDIUSB_INVALID_ARGS: "FTDIUSB: invalid arguments",
            self.COM_FTDIUSB_NOT_SUPPORTED: "FTDIUSB: not supported",
            self.COM_FTDIUSB_OTHER_ERROR: "FTDIUSB: other error",
            self.COM_PORT_ALREADY_OPEN: "Error while opening the COM port: was already open",
            self.COM_PORT_CHECKSUM_ERROR: "Checksum error in received data from COM port",
            self.COM_SOCKET_NOT_READY: "Socket not ready, you should call the function again",
            self.COM_SOCKET_PORT_IN_USE: "Port is used by another socket",
            self.COM_SOCKET_NOT_CONNECTED: "Socket not connected (or not valid)",
            self.COM_SOCKET_TERMINATED: "Connection terminated (by peer)",
            self.COM_SOCKET_NO_RESPONSE: "Can't connect to peer",
            self.COM_SOCKET_INTERRUPTED: "Operation was interrupted by a nonblocked signal",
            self.COM_PCI_INVALID_ID: "No device with this ID is present",
            self.COM_PCI_ACCESS_DENIED: "Driver could not be opened (on Vista: run as administrator!)",
            self.COM_SOCKET_HOST_NOT_FOUND: "Host not found",
            self.COM_DEVICE_CONNECTED: "Device already connected",
            self.COM_INVALID_COM_PORT: "Invalid COM port",
            self.COM_USB_DEVICE_NOT_FOUND: "USB device not found",
            self.COM_NO_USB_DRIVER: "No USB driver installed",
            self.COM_USB_NOT_SUPPORTED: "USB is not supported",
        }[self]
