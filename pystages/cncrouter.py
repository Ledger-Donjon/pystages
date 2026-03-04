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
# Values and descriptions of commands and error codes has been taken from GRBL Github repository
# https://github.com/grbl/grbl
# and the instruction manual of the CNC 3018 PRO
# https://drive.google.com/file/d/1yQH9gtO8lWbE-K0dff8g9zq_1xOB57x7
#
# Copyright 2018-2023 Ledger SAS, written by Michaël Mouchous

from __future__ import annotations

import serial.serialutil
import time
from typing import cast
from .exceptions import ConnectionFailure
from .vector import Vector
from enum import Enum
from .grbl import GRBLSetting, InvertMask, StatusReportMask
from .stage import Stage


class CNCStatus(str, Enum):
    """
    Possible statuses that the CNC can report.
    """

    IDLE = "Idle"
    RUN = "Run"
    HOLD = "Hold"
    DOOR = "Door"
    HOME = "Home"
    ALARM = "Alarm"
    CHECK = "Check"


class CNCError(Exception):
    """Exception raised when a specific error is detected by the CNC"""

    def __init__(self, message: str, cncstatus: CNCStatus):
        super().__init__(message)
        self.cncstatus = cncstatus


class CNCRouter(Stage):
    """
    Class to command CNC routers.
    """

    def __init__(self, dev: str | None = None, reset_wait_time: float = 2.0):
        """
        Open serial device to connect to the CNC routers. Raise a
        ConnectionFailure exception if the serial device could not be open.

        :param dev: Serial device. For instance `'/dev/ttyUSB0'`. If not provided, try
            to discover a suitable device according to device vendor and product IDs
        :param reset_wait_time: Depending on the state of the stage, it can take some time for
            GRBL to reset. This parameter makes the wait time to be tuned, by giving a time in seconds.
        """

        super().__init__(num_axis=3)
        self.reset_wait_time = reset_wait_time
        try:
            dev = dev or self.find_device(pid=0x7523, vid=0x1A86)
            self.serial = serial.Serial(dev, 115200, timeout=1)
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e
        self.reset_grbl()

    def reset_grbl(self, wait_time: float | None = None) -> bool:
        """
        Sends a CTRL+X control to reset the GRBL

        :return: True if the GRBL sent the correct prompt at the end of the reset
        :param wait_time: Depending on the state of the stage, it can take some time for GRBL to
            reset. This parameter makes the wait time to be tuned, by giving a time in seconds.
        """
        if wait_time is None:
            wait_time = self.reset_wait_time
        self.serial.flush()
        self.send("\030", eol="")
        time.sleep(wait_time)
        self.send("")

        responses = self.receive_lines()
        # Expected ATR is 'Grbl x.xx ['$' for help]' for first line.
        ok = responses[0].startswith("Grbl") and responses[0].endswith("['$' for help]")
        if not ok:
            return False
        # Unlock if necessary
        if "[MSG:'$H'|'$X' to unlock]" in responses:
            ok = self.unlock()
        # Force status report to send Machine Position and Work Position
        self.set_grbl_setting(
            GRBLSetting.STATUS_REPORT_MASK,
            StatusReportMask.MACHINE_POSITION | StatusReportMask.WORK_POSITION,
        )
        return ok

    def sleep(self) -> str:
        """
        Sends a `$SLP` command. The stage responds a message `[MSG:Sleeping]` after `ok`.

        :return: The response of the CNC ('ok' if command has been submitted correctly).
        """
        self.send_receive("$SLP")
        return self.receive()

    def unlock(self) -> bool:
        """
        Unlock the motor. It may happen when the stage has gone further its limits,
        and raised an alarm, or has been disabled when going in sleep mode (`$SLP`)

        :return: `True` if message `[MSG:Caution: Unlock]` has been returned
        """
        self.send("$X")
        return "[MSG:Caution: Unlocked]" in self.receive_lines()

    def get_grbl_setting(
        self, setting: GRBLSetting
    ) -> float | bool | InvertMask | StatusReportMask | int:
        return self.get_grbl_settings()[setting]

    def set_grbl_setting(
        self,
        setting: GRBLSetting,
        value: float | bool | InvertMask | StatusReportMask | int,
    ):
        """
        Set the GRBL setting of the Router with given value. The value type must correspond to
        type defined in :py:class:`GRBLSetting`.
        """
        if not isinstance(value, setting.type):
            raise ValueError(
                f"The setting {setting} expects a value of type {setting.type}."
            )
        if isinstance(value, (InvertMask, StatusReportMask)):
            # Get the int value of the flag
            value = value.value
        elif isinstance(value, bool):
            # Get the int value of the boolean (1 if true, 0 if false)
            value = 1 if value else 0
        # We do nothing for int and floats.
        return self.send_receive(f"{setting.value}={value}")

    def get_grbl_settings(
        self,
    ) -> dict[GRBLSetting, float | bool | InvertMask | StatusReportMask | int]:
        """
        Obtains and parse the list of GRBLSettings with the `$$` command.

        :return: A dictionary containing the GRBLSetting as key and its corresponding value
        """
        self.send("$$")
        lines = self.receive_lines()
        settings: dict[
            GRBLSetting, float | bool | InvertMask | StatusReportMask | int
        ] = {}
        for line in lines:
            key, value = line.split("=", 1)
            setting = GRBLSetting(key)
            if setting.type is float:
                value_float = float(value)
                settings[setting] = value_float
            else:
                # For (bool, InvertMask, StatusReportMask, int) types, str must be changed to int
                # first.
                settings[setting] = setting.type(int(value))
        return settings

    def get_current_status(self) -> tuple[CNCStatus, dict[str, object]] | None:
        """
        Sending '?' character permits to get the status of the CNC
        router

        :return: A tuple containing the status and a dictionary of all other parameters in the
            output of the command.
        """

        self.send("?", eol="")
        status = self.receive()

        # Retry once if it does not respond
        if status == "":
            self.send("?", eol="")
            status = self.receive()

        # Sometimes, the CNC returns 'ok' and the actual response is following.
        while status == "ok":
            status = self.receive()

        # In the case there is still no response after the OK
        if status == "":
            self.logger.warning("Communication error, got empty payload")
            return None

        # The possible outputs:
        # - '<Idle|MPos:1.000,3.000,4.000|FS:0,0|WCO:0.000,0.000,0.000>'
        # - 'ALARM:1'

        if status.startswith("ALARM:1"):
            # The ALARM message is followed by something like
            # '[MSG:Reset to continue]'
            next = self.receive()
            raise CNCError(next, CNCStatus.ALARM)

        # Discard any unwanted format
        if not (status.startswith("<") and status.endswith(">")):
            self.logger.warning("Response to '?' is unexpected, got '%s'", status)
            return None

        # Remove the chevrons and split all pipes.
        elements = status[1:-1].split("|")

        # First element is the CNC status
        cncstatus = CNCStatus(elements[0])

        # Next elements to be parsed as key/value pairs
        others: dict[str, object] = {}
        for key_value in [element.split(":", 1) for element in elements[1:]]:
            key = key_value[0]
            value: str | list[str] | None = (
                None if len(key_value) == 1 else key_value[1]
            )
            if isinstance(value, str) and "," in value:
                value = value.split(",")

            others[key] = value

        return cncstatus, others

    def send(self, command: str, eol: str | None = None) -> None:
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
        Receive multiple lines until getting as specific value.

        :param until: The expected response indicating the end of received lines.
        :return: The list of all received lines. Note that the expected line is not included in the
            list.
        """
        lines: list[str] = []
        while (line := self.serial.readline().strip().decode()) != until:
            if len(line):
                lines.append(line)
        return lines

    def receive(self) -> str:
        """
        Read input serial buffer to get a response. Blocks until a response is
        available.

        :return: Received response string, CR-LF removed.
        """
        tries = 10
        # Read at least 2 bytes for CR-LF.
        response = self.serial.read(2)
        while response[-2:] != b"\r\n":
            part = self.serial.read(1)
            response += part
            # Give a chance to get out of this
            if part == b"":
                tries -= 1
            if tries == 0:
                return ""
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
        max_attempts = 20  # ~1s with 50ms sleep
        attempts = 0
        while attempts < max_attempts:
            status_tuple = self.get_current_status()
            if status_tuple is None:
                attempts += 1
                time.sleep(0.05)
                continue
            extra_dict: dict[str, object] = status_tuple[1]
            # Preferred: compute WPos = MPos - WCO when both available
            if "WCO" in extra_dict and "MPos" in extra_dict:
                mpos_raw = extra_dict.get("MPos")
                wco_raw = extra_dict.get("WCO")
                if isinstance(mpos_raw, list) and isinstance(wco_raw, list):
                    mpos_src = cast(list[str], mpos_raw)
                    wco_src = cast(list[str], wco_raw)
                    mpos_list: list[float] = [float(v) for v in mpos_src]
                    wco_list: list[float] = [float(v) for v in wco_src]
                    mpos = Vector(*mpos_list)
                    wco = Vector(*wco_list)
                    return mpos - wco
            # Fallback: if WPos is directly available, use it
            if "WPos" in extra_dict:
                wpos_raw = extra_dict.get("WPos")
                if isinstance(wpos_raw, list):
                    wpos_src = cast(list[str], wpos_raw)
                    wpos_list: list[float] = [float(v) for v in wpos_src]
                    return Vector(*wpos_list)
            attempts += 1
            time.sleep(0.05)

        # If we reach here, we were unable to retrieve a usable status
        raise ConnectionFailure(
            "Unable to read CNC position: status unavailable or missing fields."
        )

    @position.setter
    def position(self, value: Vector):
        # To check dimension and range of the given value
        pos_setter = cast(property, Stage.position).fset
        assert pos_setter is not None
        pos_setter(self, value)

        coords: list[float] = [float(v) for v in cast(list[float], value.data)]
        command = f"G0 X{coords[0]}"
        if len(coords) > 1:
            command += f" Y{coords[1]}"
        if len(coords) > 2:
            command += f" Z{coords[2]}"
        self.send_receive(command)

    @property
    def is_moving(self) -> bool:
        """
        Queries the current status of the CNC in order to determine if the CNC is moving

        :return: True if the CNC reports that a cycle is running (Run) or
            if it is in a middle of a homing cycle (Home).
        """
        # Avoid busy-wait infinite loop if the device is unresponsive
        for _ in range(10):
            status = self.get_current_status()
            if status is not None:
                return status[0] in [CNCStatus.RUN, CNCStatus.HOME]
            time.sleep(0.05)
        # If status is consistently unavailable, consider not moving
        return False

    def set_origin(self) -> str:
        """
        Set current position as origin

        :return: The response of the CNC ('ok' if command has been submitted correctly).
        """
        return self.send_receive("G92 X0 Y0 Z0")

    def home(self, wait: bool = False):
        """
        Sends a `$H` command. The stage responds a message `[MSG:Sleeping]` after `ok`.
        Take caution for collisions before calling this method !

        :param wait: Optionally waits for move operation to be done.
        """
        self.send("$H")
        if wait:
            self.wait_move_finished()
