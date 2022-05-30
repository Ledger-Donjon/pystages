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


import serial
from binascii import hexlify
from .exceptions import ConnectionFailure, ProtocolError, VersionNotSupported
from .stage import Stage


class M3FS(Stage):
    """
    Class to command New Scale Technologies M3-FS focus modules in serial mode
    (VCP).
    If a M3-FS device is seen as a USBXpress chip, it may be used as a
    Virtual-Com-Port after a few cumbersome operations (custom driver with
    correct VID/DID).
    """

    def __init__(self, dev):
        """
        Connect to the device. If the serial device cannot be opened, a
        ConnectionFailure exception is thrown. If the device version is not
        supported, a VersionNotSupported error is thrown.

        :param dev: Serial device. For instance 'COM0'.
        """
        super().__init__()
        self.resolution_um = 0.5
        try:
            self.serial = serial.Serial(
                dev, baudrate=250000, stopbits=serial.STOPBITS_TWO
            )
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e
        # Test version string.
        # Currently, only one version has been tested. Some others may be added
        # in the future...
        self.serial.timeout = 1
        try:
            res = self.command(1)
        except ProtocolError as e:
            raise ConnectionFailure() from e
        self.serial.timeout = None
        if res != "1 VER 4.7.3 M3-FS":
            raise VersionNotSupported(res)

    def __send(self, command, data=None):
        """
        Send a command to the controller.

        :param command: Command integer ID.
        :param data: Extra data string.
        """
        if data is not None:
            assert ("<" not in data) and (">" not in data) and ("\r" not in data)
        if command not in range(100):
            raise ValueError("Invalid command ID.")
        full_command = "<{0:02d}".format(command)
        if data is not None:
            full_command += " " + data
        full_command += ">\r"
        self.serial.write(full_command.encode())

    def __receive(self):
        """
        Read next response from the controller.

        :return: Response string, without '<', '>' and carriage return.
        """
        # Get start '<'
        b = self.serial.read(1)
        if len(b) != 1:
            raise ProtocolError()
        if b[0] != ord("<"):
            raise ProtocolError()
        # Get the response bytes until '>'
        result = bytearray()
        while True:
            b = self.serial.read(1)
            if len(b) != 1:
                raise ProtocolError()
            b = b[0]
            if b == ord(">"):
                break
            else:
                if b == ord("\r"):
                    raise ProtocolError()
                result.append(b)
        # Get carriage return
        b = self.serial.read(1)
        if len(b) != 1:
            raise ProtocolError()
        if b[0] != ord("\r"):
            raise ProtocolError()
        return result.decode()

    def command(self, command, data=None):
        """
        Send a command to the controller and get the response.

        :param command: Command integer ID.
        :param data: Extra data string.
        :return: Response data string.
        """
        self.__send(command, data)
        res = self.__receive()
        # Check that the command id in the response is the same as the command
        # id in the request.
        if (len(res) < 2) or (int(res[0:2]) != command):
            raise ProtocolError()
        if len(res) == 2:
            return None
        else:
            if res[2] != " ":
                raise ProtocolError()
            return res[3:]

    def __get_closed_loop_status(self):
        """
        Query closed-loop status and position.

        :return: Tuple of 3 int.
        """
        res = list(bytes.fromhex(x) for x in self.command(10).split(" "))
        motor_status = int.from_bytes(res[0], "big", signed=False)
        position = int.from_bytes(res[1], "big", signed=True)
        error = int.from_bytes(res[2], "big", signed=True)
        return motor_status, position, error

    @property
    def position(self):
        """
        Stage position, in micrometers.

        :getter: Query and return current stage position.
        :setter: Move stage. Wait until position is reached.
        """
        motor_status, position, error = self.__get_closed_loop_status()
        return position * self.resolution_um

    @position.setter
    def position(self, value):
        val = round(value / self.resolution_um).to_bytes(4, "big", signed=True)
        self.command(8, hexlify(val).decode())
        # Now wait until motor is not moving anymore
        while self.__get_closed_loop_status()[0] & 4:
            pass
