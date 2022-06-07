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
import time
from typing import Optional

import serial
from .exceptions import ConnectionFailure
from .vector import Vector
from enum import Enum
from .grbl import GRBLSetting
from .stage import Stage


class CNCStatus(Enum):
    IDLE = "Idle"
    RUN = "Run"
    HOLD = "Hold"
    DOOR = "Door"
    HOME = "Home"
    ALARM = "Alarm"
    CHECK = "Check"


class CNCRouter(Stage):
    """
    Class to command CNC routers.
    """

    def __init__(self, dev: str):
        """
        Open serial device to connect to the CNC routers. Raise a
        ConnectionFailure exception if the serial device could not be open.

        :param dev: Serial device. For instance '/dev/ttyUSB0'.
        """
        super().__init__(num_axis=3)
        try:
            self.serial = serial.Serial(dev, 115200)
            self.timeout = 1
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e
        self.reset_grbl()

    def reset_grbl(self) -> bool:
        """
        Sends a CTRL+X control to reset the GRBL
        :return: True if the GRBL sends the correct prompt
        """
        self.serial.flush()
        self.send("\030", eol="")
        time.sleep(0.05)
        self.send("")

        responses = self.receive_lines()
        # Expected ATR is 'Grbl x.xx ['$' for help]' for first line.
        ok = responses[0].startswith("Grbl") and responses[0].endswith("['$' for help]")
        if not ok:
            return False
        # Unlock if necessary
        if "[MSG:'$H'|'$X' to unlock]" in responses:
            ok = self.unlock()
        return ok

    def sleep(self):
        """
        Sends a $SLP command. The stage responds a message '[MSG:Sleeping]' after 'ok'.
        """
        self.send_receive("$SLP")
        return self.receive()

    def unlock(self) -> bool:
        """
        Unlock the motor. It may happen when the stage has gone further its limits,
        and raised an alarm, or has been disabled when going in sleep mode ('$SLP')
        :return: True if message [MSG:Caution: Unlock] has been returned
        """
        self.send("$X")
        return "[MSG:Caution: Unlocked]" in self.receive_lines()

    def get_grbl_settings(self) -> dict:
        """
        Obtains and parse the list of GRBLSettings with the '$$' command.
        :return: A dictionary containing the GRBLSetting as key and its corresponding value
        """
        self.send("$$")
        lines = self.receive_lines()
        settings = {}
        for line in lines:
            key, value = line.split("=", 1)
            setting = GRBLSetting(key)
            if setting.type == float:
                value = float(value)
                settings[setting] = value
            else:
                settings[setting] = setting.type(int(value))
        return settings

    def get_current_status(self) -> Optional[tuple[CNCStatus, dict]]:
        """
        Sending '?' character permits to get the status of the CNC
        router
        :return: A tuple containing the status and a dictionary of all other
        parameters in the output of the command.
        """
        self.send("?", eol="")
        status = self.receive()
        # The output
        # '<Idle|MPos:1.000,3.000,4.000|FS:0,0|WCO:0.000,0.000,0.000>'
        # Remove the chevrons
        status = status[1:-1]
        elements = status.split("|")

        # First element is the CNC status
        cncstatus = CNCStatus(elements[0])

        # Next elements to be parsed as key/value pairs
        others = {}
        for key_value in [element.split(":", 1) for element in elements[1:]]:
            key = key_value[0]
            value = None if len(key_value) == 1 else key_value[1]
            if value is not None and "," in value:
                value = value.split(",")

            others[key] = value

        return cncstatus, others

    def send(self, command: str, eol=None):
        """
        Send a command.

        :param command: Command string.
        :param eol: End of command character(s). If None, LF will be automatically append.
        """
        if eol is None:
            eol = "\n"
        self.serial.write((command + eol).encode())

    def receive_lines(self, until: str = "ok") -> list[str]:
        """
        Receive multiple lines until getting as specific value
        :param until:
        :return:
        """
        lines = []
        while (l := self.serial.readline().strip().decode()) != until:
            if len(l):
                lines.append(l)
        return lines

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

        :param command: Command string.
        :return: Received response string, CR-LF removed.
        """
        self.send(command)
        return self.receive()

    @property
    def position(self) -> Vector:
        """
        Current stage position. Vector.

        :getter: Query and return stage position.
        :setter: Move the stage.
        """
        res = self.get_current_status()[1]["MPos"]
        return Vector(*tuple(float(x) for x in res))

    @position.setter
    def position(self, value: Vector):
        # To check dimension and range of the given value
        super(__class__, self.__class__).position.fset(self, value)

        command = f"G0 X{value.x}"
        if len(value) > 1:
            command += f" Y{value.y}"
        if len(value) > 2:
            command += f" Z{value.z}"
        self.send_receive(command)

    @property
    def is_moving(self) -> bool:
        """Queries the current status of the CNC in order to determine if the CNC is moving"""
        status = self.get_current_status()[0]
        return status in [CNCStatus.RUN, CNCStatus.HOME]

    def set_origin(self):
        """
        Set current position as origin
        :return:
        """
        return self.send_receive("G92 X0 Y0 Z0")
