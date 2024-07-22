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
# Copyright 2018-2022 Ledger SAS, written by Olivier Hériveaux


import serial.serialutil
import time
from .exceptions import ConnectionFailure
from .vector import Vector
from .stage import Stage
from typing import Optional


class Corvus(Stage):
    """
    Class to command Corvus Eco XYZ stage controller.
    """

    def __init__(self, dev: Optional[str] = None, serial_number: Optional[str] = None):
        """
        Open serial device to connect to the Corvus controller. Raise a
        ConnectionFailure exception if the serial device could not be open.

        :param dev: Serial device path. For instance '/dev/ttyUSB0'.
        :param serial_number: Device Serial Number. For instance 'A600AAAA'.
        """
        super().__init__(num_axis=3)
        try:
            dev = dev or self.find_device(serial_number=serial_number)
            self.serial = serial.Serial(dev, 57600)
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e
        self.__init()

    def __init(self):
        """Initialize a few parameters."""
        # Tell we work with 3 axis for move commands
        self.send("3 setdim")
        # Set unit to micrometers, for all axis
        unit = 1
        self.send("{0} -1 setunit".format(unit))
        # Verify it has been taken into account (this can be dangerous
        # otherwise)
        res = self.send_receive("-1 getunit").split()
        for x in res:
            assert int(x) == unit
        # Enable joystick
        self.enable_joystick()

    def send(self, command: str):
        """
        Send a command.

        :param command: Command string. CR or blank must not be present at the
            end of this string.
        """
        self.serial.write((command + " ").encode())

    def receive(self) -> str:
        """
        Read input serial buffer to get a response. Blocks until a response is
        available.

        :return: Received response string, CR-LF removed.
        """
        # Read at least 2 bytes for CR-LF.
        response = self.serial.read(2)
        while response[-2:] != b"\r\n":
            response += self.serial.read(1)
        # Remove CR-LF and return as string
        return response[:-2].decode()

    def send_receive(self, command: str) -> str:
        """
        Send a command, wait and return the response.

        :param command: Command string. CR or blank must not be present at the
            end of this string.
        :return: Received response string, CR-LF removed.
        """
        self.send(command)
        return self.receive()

    def calibrate_xy(self):
        """
        Execute limit-switch move only on X and Y axises. Wait until
        calibration si done.
        Take caution for collisions before calling this method !
        """
        # Disable Z-axis
        self.send("3 3 setaxis")
        # Call for calibration
        self.send("cal")
        self.send("rm")
        # Wait until finished
        for i in range(2):
            while int(self.send_receive("{0} getcaldone".format(i + 1))) != 3:
                time.sleep(0.1)
        # Re-enabled Z-axis
        self.send("1 3 setaxis")

    def calibrate(self):
        """
        Execute limit-switch move. Wait until calibration is done.
        Take caution for collisions before calling this method !
        """
        # Call for calibration
        self.send("cal")
        self.send("rm")
        # Wait until finished
        for i in range(3):
            while int(self.send_receive("{0} getcaldone".format(i + 1))) != 3:
                time.sleep(0.1)

    def home(self, wait=False):
        """
        Execute limit-switch move.
        Take caution for collisions before calling this method !

        :param wait: Optionally waits for move operation to be done.
        """
        # Call for calibration
        self.send("cal")
        if wait:
            self.wait_move_finished()

    def move_relative(self, x, y, z):
        """
        Move stage relative to current position.

        :param x: Relative distance on X-axis, in micrometers.
        :param y: Relative distance on Y-axis, in micrometers.
        :param z: Relative distance on Z-axis, in micrometers.
        """
        self.send("3 setdim")
        self.send("{0} {1} {2} rmove".format(x, y, z))
        self.wait_move_finished()

    @property
    def is_moving(self):
        return bool(int(self.send_receive("st")) & 1)

    def set_origin(self):
        """Set current stage's coordinates as the new origin."""
        self.send("0 0 0 setpos")

    def enable_joystick(self):
        """Enable joystick (manual mode)"""
        self.send("1 j")

    @property
    def is_connected(self):
        """:return: True if the instance is connected to the stage."""
        return self.serial is not None

    @property
    def position(self):
        """
        Current stage position. Vector.

        :getter: Query and return stage position.
        :setter: Move the stage.
        """
        res = self.send_receive("p").split()
        return Vector(*tuple(float(x) for x in res))

    @position.setter
    def position(self, value: Vector):
        # To check dimension and range of the given value
        pos_setter = Stage.position.fset
        assert pos_setter is not None
        pos_setter(self, value)

        self.send("3 setdim")
        self.send("{0} {1} {2} move".format(value.x, value.y, value.z))

    @property
    def velocity(self):
        """
        Motors velocity setting, in µm/s.

        :getter: Query and return current setting.
        :setter: Update controller setting.
        """
        res = float(self.send_receive("gv"))
        return res

    @velocity.setter
    def velocity(self, value):
        if value < 0:
            raise ValueError("Velocity parameter cannot be negative.")
        self.send("{0} sv".format(value))

    @property
    def acceleration(self):
        """
        Motors acceleration setting, in µm/s^2.

        :getter: Query and return current setting.
        :setter: Update controller setting.
        """
        res = float(self.send_receive("ga"))
        return res

    @acceleration.setter
    def acceleration(self, value):
        if value < 0:
            raise ValueError("Acceleration parameter cannot be negative.")
        self.send("{0} sa".format(value))

    def save(self):
        """Save current parameters in non-volatile memory."""
        self.send("save")

    def restore(self):
        """
        Reactivates the last saved parameters. Beware this might change units,
        which may be dangerous if care is not taken.
        """
        self.send("restore")
