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

from __future__ import annotations

import serial.serialutil
import time
from typing import cast
from enum import Enum
from .exceptions import ConnectionFailure, ProtocolError
from .vector import Vector
from .stage import Stage
from .pi_errors import PIError


class PIReferencingMethod(int, Enum):
    """
    Enum for PI reference methods.
    """

    POS_ALLOWED = 0  # An absolute position value can be assigned with POS, or a referencing move can be started with FRF, FNL or FPL.
    REFERENCING_ONLY = 1  # A referencing move must be started with FRF, FNL or FPL. Using POS is not allowed.


class PI(Stage):
    """
    Class to control PI stages.
    """

    def __init__(
        self,
        dev: str | None = None,
        baudrate: int = 115200,
        addresses: list[int] | None = None,
    ) -> None:
        """
        Initialize the PI stage.

        :param dev: Serial device string (for instance `'/dev/ttyUSB0'` or
            'COM0'), an instance of Link, or an instance of SMC100 sharing
            the same serial device.
            If not provided, a suitable device is searched according to
            according to vendor and product IDs
        :param baudrate: Baudrate for the serial connection.
        :param addresses: An iterable of int controller addresses.
        """
        if addresses is None:
            addresses = [1]

        super().__init__(num_axis=len(addresses))
        self.addresses = addresses
        try:
            dev = dev or self.find_device(pid=0x1007, vid=0x1A72)
            self.serial = serial.Serial(dev, baudrate=baudrate, timeout=1)
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e
        self.logger.debug(f"Connected to PI stage at {dev=}")
        self._idns = self.idn()

    def send(self, address: int | None, command: str) -> None:
        """
        Send a command to the stage.
        """
        cmd = f"{address} " if address is not None else ""
        cmd += f"{command}\n"
        self.logger.debug(f"> {cmd.strip()}")
        self.serial.write(cmd.encode("utf-8"))

    def fast_query(self, address: int, command: int) -> list[str]:
        """
        Single-character commands, e.g., fast query commands, consist only of one ASCII
        character.

        :param address: The address of the stage.
        :param command: The command to send.
        :return: The response from the stage.
        """
        command_str = chr(command)
        self.logger.debug(f"> {address} #{command}")
        self.serial.write(f"{address} {command_str}".encode("utf-8"))
        response = self.serial.readline().decode("utf-8").strip()
        self.logger.debug(f"< {response}")
        response_list = response.split(" ", 2)
        if len(response_list) != 3:
            raise ProtocolError(
                query=f"{address} #{command}",
                response=response,
            )
        if int(response_list[0]) != 0:
            raise ProtocolError(
                query=f"{address} #{command}",
                response=response,
            )
        if int(response_list[1]) != address:
            raise ProtocolError(
                query=f"{address} #{command}",
                response=response,
            )
        return response_list

    def query(
        self,
        command: str,
        address: int | None = None,
        args: list[str] | None = None,
    ) -> list[str]:
        """
        Send a command to the stage and return the response.

        :param command: The command to send.
        :param address: The address of the stage.
        :param args: The arguments to send (if any).
        :return: The response from the stage.
        """
        cmd = f"{address} " if address is not None else ""
        cmd += f"{command}?"
        cmd += " " + " ".join(args) if args else ""
        cmd += "\n"
        self.logger.debug(f"> {cmd.strip()}")
        try:
            self.serial.write(cmd.encode("utf-8"))
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure(
                f"Failed to write command '{cmd.strip()}' to the serial device."
            ) from e
        responses: list[str] = []
        while True:
            _response = self.serial.readline().decode("utf-8").rstrip("\r\n")
            self.logger.debug(f"< {_response}")
            if address is not None and len(responses) == 0:
                response = _response.split(" ", 2)
                # In the case the query contains a specific Target address,
                # the first line of the response is split into 3 parts:
                # 0: Sender address of the query (PC, always 0)
                # 1: Target address of the query (PI GCS)
                # 2: Payload
                if (
                    len(response) != 3
                    or int(response[0]) != 0
                    or int(response[1]) != address
                ):
                    raise ProtocolError(
                        query=cmd,
                        response=_response,
                    )

                payload: str = response[2]
            else:
                payload = _response
            responses.append(payload.strip())
            # PI GCS: trailing space before CRLF indicates more lines follow
            if not payload.endswith(" "):
                break
        return responses

    def idn(self) -> list[str]:
        """
        Get the ID of the stage.

        :return: The ID of the stage.
        """
        results: list[str] = []
        for address in self.addresses:
            results += self.query("*IDN", address)
        return results

    @property
    def position(self) -> Vector:
        """
        Get the position of the stage.

        :return: The position of the stage.
        """
        positions: list[float] = []
        for a in self.addresses:
            res = self.query("POS", a)[0]
            response = res.split("=")
            if len(response) != 2 or int(response[0]) != 1:
                raise ProtocolError(
                    query=f"{a} POS",
                    response=res,
                    expected="1=POSITION",
                )
            positions.append(float(response[1].strip()))
        return Vector(*positions)

    @position.setter
    def position(self, value: Vector) -> None:
        # To check dimension and range of the given value
        pos_setter = cast(property, Stage.position).fset
        assert pos_setter is not None
        pos_setter(self, value)

        for i, pos in enumerate(value.data):
            if i >= len(self.addresses):
                break
            address = self.addresses[i]
            self.move(address, pos)

    def move(self, address: int, position: float) -> None:
        """
        Move the stage to the specified position.

        :param address: The address of the stage.
        :param position: The position to move to.
        """
        self.send(address, f"MOV 1 {position}")

    @property
    def is_moving(self) -> bool:
        """
        Check if the stage is moving.

        :param address: The address of the stage.
        :return: True if the stage is moving, False otherwise.
        """
        for address in self.addresses:
            # self.serial.write(f"{address} \x05".encode("utf-8"))
            # response = self.serial.readline().decode("utf-8").strip().split(" ", 2)
            response = self.fast_query(address, 0x05)
            if response[2] != "0":
                return True
        return False

    @property
    def reference_methods(self) -> list[PIReferencingMethod]:
        """
        Get the reference methods.

             0: An absolute position value can be assigned with POS,
                or a referencing move can be started with FRF, FNL or FPL.
             1 (default): A referencing move must be started with FRF, FNL or FPL.
                Using POS is not allowed.
        """
        reference_methods: list[PIReferencingMethod] = []
        for address in self.addresses:
            # 0: An absolute position value can be assigned with POS,
            #    or a referencing move can be started with FRF, FNL or FPL.
            # 1 (default): A referencing move must be started with FRF, FNL or FPL.
            #    Using POS is not allowed.
            reference_method: str = self.query("RON", address)[0].split("=")[1]
            reference_methods.append(PIReferencingMethod(int(reference_method)))
            self.logger.debug(f"For device at {address}: {reference_method=}")
        return reference_methods

    @reference_methods.setter
    def reference_methods(
        self, value: list[PIReferencingMethod] | PIReferencingMethod
    ) -> None:
        """
        Set the reference methods.

        :param value: A list of PIReferencingMethod.
        """
        if isinstance(value, PIReferencingMethod):
            value = [value] * len(self.addresses)

        for address, method in zip(self.addresses, value):
            self.send(address, f"RON 1 {method.value}")
            self.logger.debug(
                f"Set reference method for device at {address=}: {method.value=}"
            )

    def fast_reference(self, negative_limit: bool = True) -> None:
        """
        Perform a fast reference move.

        Moves the specified axis to the positive or negative physical
        limit of its travel range and sets the current position to a defined
        value.

        :param negative_limit: If True, move to the negative limit. If False, move to the positive limit.
        """
        for address in self.addresses:
            # Set the servo mode to on (closed-loop operation)
            self.send(address, "SVO 1 1")
            self.send(address, f"{'FNL' if negative_limit else 'FPL'} 1")
            self.logger.debug(f"Performed fast reference for device at {address=}")

    def is_reference_needed(self) -> bool:
        """
        Check if a reference move is needed for at least one axis.

        :return: True if a reference move is needed, False otherwise.
        """
        for address in self.addresses:
            # 1 = Referencing has been done
            # 0 = Referencing has not been done
            if not self.query("FRF", address)[0].split("=")[1] == "1":
                return True
        return False

    def home(self, wait: bool = False) -> None:
        """
        Move the stage to the home position (make a reference to low limit).

        :param wait: If True, wait for the stage to reach the home position.
        """
        self.fast_reference()
        if wait:
            while self.is_moving:
                time.sleep(0.1)

    def stop(self) -> None:
        """
        Stop the stage.
        """
        for address in self.addresses:
            self.send(address, "STP")

    def error(self) -> list[PIError]:
        """
        Get the error status of the stage.

        :return: The error status of the stage.
        """
        errors: list[PIError] = []
        for address in self.addresses:
            response = self.query("ERR", address)
            if len(response) != 1:
                raise ProtocolError(
                    query=f"{address} ERR?",
                    response=" ".join(response),
                )
            try:
                error_code_int = int(response[0])
            except ValueError:
                raise ProtocolError(
                    query=f"{address} ERR?",
                    response=response[0],
                    expected="'ERROR', with ERROR being an integer",
                )
            if error_code_int not in PIError.__members__.values():
                raise ProtocolError(
                    query=f"{address} ERR?",
                    response=response[0],
                    expected=f"An integer within the list of {list(PIError.__members__.values())}",
                )
            errors.append(PIError(error_code_int))
        return errors

    def set_origin(self) -> None:
        """
        Set current stage's coordinates as the new origin.
        """
        for address in self.addresses:
            try:
                response = self.serial.write(f"{address} POS 1 0\n".encode("utf-8"))
                # self.send(address, "POS 1 0")
            except serial.serialutil.SerialException as exc:
                raise ConnectionFailure(
                    f"Failed to set origin for device at address {address}"
                ) from exc
            if not response:
                raise ConnectionFailure(
                    f"No response received when setting origin for device at address {address}"
                )
