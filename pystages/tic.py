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
#
# Copyright 2018-2020 Ledger SAS, written by Olivier Hériveaux


import usb.core
import usb.util
from enum import Enum
from time import sleep


class TicVariable(Enum):
    """
    Variables which can be read using GET_VARIABLE command.
    https://www.pololu.com/docs/0J71/7
    """
    # Each value is a (offset, size, signed) tuple
    OPERATION_STATE = (0x00, 1, False)
    MISC_FLAGS = (0x01, 1, False)
    ERROR_STATUS = (0x02, 2, False)
    ERRORS_OCCURRED = (0x04, 4, False)
    PLANNING_MODE = (0x09, 1, False)
    TARGET_POSITION = (0x0a, 4, True)
    TARGET_VELOCITY = (0x0e, 4, True)
    STARTING_SPEED = (0x12, 4, False)
    MAX_SPEED = (0x16, 4, False)
    MAX_DECELERATION = (0x1a, 4, False)
    MAX_ACCELERATION = (0x1e, 4, False)
    CURRENT_POSITION = (0x22, 4, True)
    CURRENT_VELOCITY = (0x26, 4, True)
    ACTING_TARGET_POSITION = (0x2a, 4, True)
    TIME_SINCE_LAST_STEP = (0x2e, 4, False)
    DEVICE_RESET = (0x32, 1, False)
    VIN_VOLTAGE = (0x33, 2, False)
    UP_TIME = (0x35, 4, False)
    ENCODER_POSITION = (0x39, 4, True)
    RC_PULSE_WIDTH = (0x3d, 2, False)
    ANALOG_READING_SCL = (0x3f, 2, False)
    ANALOG_READING_SDA = (0x41, 2, False)
    ANALOG_READING_TX = (0x43, 2, False)
    ANALOG_READING_RX = (0x45, 2, False)
    DIGITAL_READINGS = (0x47, 1, False)
    PIN_STATES = (0x48, 1, False)
    STEP_MODE = (0x49, 1, False)
    CURRENT_LIMIT = (0x4a, 1, False)
    DECAY_MODE = (0x4b, 1, False)
    INPUT_STATE = (0x4c, 1, False)
    INPUT_AFTER_AVERAGING = (0x4d, 2, False)
    INPUT_AFTER_HYSTERESIS = (0x4f, 2, False)
    INPUT_AFTER_SCALING = (0x51, 4, True)
    LAST_MOTOR_DRIVER_ERROR = (0x55, 1, False)
    AGC_MODE = (0x56, 1, False)
    AGC_BOTTOM_CURRENT_LIMIT = (0x57, 1, False)
    AGC_CURRENT_BOOST_STEP = (0x58, 1, False)
    AGC_FREQUENCY_LIMIT = (0x59, 1, False)
    LAST_HP_DRIVER_ERRORS = (0xff, 1, False)


class TicCommand(Enum):
    """
    Command codes for Polulu Tic Stepper Motor Controller.
    https://www.pololu.com/docs/0J71/8
    """
    SET_TARGET_POSITION = 0xe0
    SET_TARGET_VELOCITY = 0xe3
    HALT_AND_SET_POSITION = 0xec
    HALT_AND_HOLD = 0x89
    GO_HOME = 0x97
    RESET_COMMAND_TIMEOUT = 0x8c
    DEENERGIZE = 0x86
    ENERGIZE = 0x85
    EXIT_SAFE_START = 0x83
    ENTER_SAFE_START = 0x8f
    RESET = 0xb
    CLEAR_DRIVER_ERROR = 0x8a
    SET_MAX_SPEED = 0xe6
    SET_STARTING_SPEED = 0xe5
    SET_MAX_ACCELERATION = 0xea
    SET_MAX_DECELERATION = 0xe9
    SET_STEP_MODE = 0x94
    SET_CURRENT_LIMIT = 0x91
    SET_DECAY_MODE = 0x92
    SET_AGC_OPTION = 0x98
    GET_VARIABLE = 0xa1
    GET_VARIABLE_AND_CLEAR_ERRORS_OCCURRED = 0xa2
    GET_SETTING = 0xa8
    SET_SETTING = 0x13
    REINITIALIZE = 0x10
    START_BOOTLOADER = 0xff


class TicDirection(Enum):
    """ Possible directions for homing """
    REVERSE = 0
    FORWARD = 1


class Tic:
    """
    Very basic driver class for Polulu Tic Stepper Motor controller, connected
    in USB.
    """
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x1ffb, idProduct=0x00b5)
        self.dev.set_configuration()
        self.energize()

    def quick(self, command: TicCommand):
        """
        Send a quick command with no data.

        :param command: Command.
        """
        self.dev.ctrl_transfer(0x40, command.value, 0, 0, 0)

    def write_7(self, command: TicCommand, data):
        """
        Write 7 bits.

        :param command: Command.
        :param data: Value to be written.
        """
        self.dev.ctrl_transfer(0x40, command.value, data, 0, 0)

    def write_32(self, command: TicCommand, data):
        """
        Write 32 bits.

        :param command: Command code.
        :param data: Value to be written.
        """
        self.dev.ctrl_transfer(
            0x40, command.value, data & 0xffff, data >> 16, 0)

    def block_read(self, command: TicCommand, offset, length):
        """
        Read data from the device.

        :param command: Command code.
        :param offset: Data offset.
        :param length: Data length.
        """
        return bytes(
            self.dev.ctrl_transfer(0xc0, command.value, 0, offset, length))

    def set_setting(self, command: TicCommand, data, offset):
        """
        Set setting data.

        :param command: Command code.
        :param data: Value to be written.
        :param offset: Write offset.
        """
        self.dev.ctrl_transfer(0x40, command.value, data, offset, 0)

    def energize(self):
        self.quick(TicCommand.ENERGIZE)

    def deenergize(self):
        self.quick(TicCommand.DEENERGIZE)

    def reset(self):
        self.quick(TicCommand.RESET)

    def exit_safe_start(self):
        self.quick(TicCommand.EXIT_SAFE_START)

    def go_home(self, direction: TicDirection, wait: bool = True):
        """
        Run the homing procedure.
        :param direction: Homing direction.
        :param wait: If True, wait for homing procedure end.
        """
        self.write_7(TicCommand.GO_HOME, direction.value)
        if wait:
            while self.get_variable(TicVariable.MISC_FLAGS) & (1 << 4):
                sleep(0.1)
                self.exit_safe_start()

    def set_target_position(self, pos):
        self.write_32(TicCommand.SET_TARGET_POSITION, pos)

    def set_target_velocity(self, velocity):
        self.write_32(TicCommand.SET_TARGET_VELOCITY, velocity)

    def get_variable(self, variable: TicVariable):
        offset, length, signed = variable.value
        return int.from_bytes(
            self.block_read(TicCommand.GET_VARIABLE, offset, length),
            'little', signed=signed)

    @property
    def position(self):
        """ Motor position, in steps. """
        return self.get_variable(TicVariable.CURRENT_POSITION)

    @property
    def target_position(self):
        return self.get_variable(TicVariable.TARGET_POSITION)

    @target_position.setter
    def target_position(self, value):
        self.set_target_position(value)
