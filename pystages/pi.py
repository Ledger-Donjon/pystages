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

import serial.serialutil
import time
from typing import Optional, List, Union
from .exceptions import ConnectionFailure
from .vector import Vector
from .stage import Stage
from .pi_errors import PIError
from enum import Enum


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
        dev: Optional[str] = None,
        baudrate: int = 115200,
        addresses: List[int] = [1],
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
        super().__init__(num_axis=len(addresses))
        self.addresses = addresses
        try:
            dev = dev or self.find_device(pid=0x1007, vid=0x1A72)
            self.serial = serial.Serial(dev, baudrate=baudrate, timeout=1)
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e
        # print("Connected to PI stage at", dev)
        self._idns = self.idn()

    def query(
        self, command: str, address: Optional[int] = None, args=None
    ) -> List[str]:
        """
        Send a command to the stage and return the response.

        :param address: The address of the stage.
        :param command: The command to send.
        :return: The response from the stage.
        """
        cmd = f"{address} " if address is not None else ""
        cmd += f"{command}?"
        cmd += " " + " ".join(args) if args else ""
        cmd += "\n"
        # print(">", cmd.strip())
        try:
            self.serial.write(cmd.encode("utf-8"))
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure(
                f"Failed to write command '{cmd.strip()}' to the serial device."
            ) from e
        responses = []
        while True:
            _response = self.serial.readline().decode("utf-8").strip()
            # print("<", repr(_response))
            response = _response.split(" ", 2)
            assert (
                len(response) == 3
                and int(response[0]) == 0
                and int(response[1]) == address
            ), (
                f"Unexpected format of response: '{_response}', expecting '0 {address} PAYLOAD'."
            )

            payload: str = response[2].strip()
            responses.append(payload)
            if not payload.endswith(" \n"):
                break
        return responses

    def idn(self) -> List[str]:
        """
        Get the ID of the stage.

        :return: The ID of the stage.
        """
        results = []
        for address in self.addresses:
            results += self.query("*IDN", address)
        return results

    @property
    def position(self) -> Vector:
        """
        Get the position of the stage.

        :return: The position of the stage.
        """
        positions = []
        for a in self.addresses:
            response = self.query("POS", a)[0]
            response = response.split("=")
            assert len(response) == 2
            assert int(response[0]) == 1
            positions.append(float(response[1].strip()))
        return Vector(*positions)

    @position.setter
    def position(self, value: Vector):
        # To check dimension and range of the given value
        pos_setter = Stage.position.fset
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
        cmd = f"{address} MOV 1 {position}\n"
        # print("Move command:", cmd)
        self.serial.write(cmd.encode("utf-8"))

    @property
    def is_moving(self) -> bool:
        """
        Check if the stage is moving.

        :param address: The address of the stage.
        :return: True if the stage is moving, False otherwise.
        """
        for address in self.addresses:
            self.serial.write(f"{address} \x05".encode("utf-8"))
            response = self.serial.readline().decode("utf-8").strip().split(" ", 2)
            assert len(response) == 3
            assert int(response[0]) == 0
            assert int(response[1]) == address
            if response[2] != "0":
                return True
        return False

    @property
    def reference_methods(self):
        """
        Get the reference methods.

             0: An absolute position value can be assigned with POS,
                or a referencing move can be started with FRF, FNL or FPL.
             1 (default): A referencing move must be started with FRF, FNL or FPL.
                Using POS is not allowed.
        """
        reference_methods: List[PIReferencingMethod] = []
        for address in self.addresses:
            # 0: An absolute position value can be assigned with POS,
            #    or a referencing move can be started with FRF, FNL or FPL.
            # 1 (default): A referencing move must be started with FRF, FNL or FPL.
            #    Using POS is not allowed.
            reference_method: str = self.query("RON", address)[0].split("=")[1]
            reference_methods.append(PIReferencingMethod(int(reference_method)))
            # print(f"For device at {address}: {reference_method=}")
        return reference_methods

    @reference_methods.setter
    def reference_methods(
        self, value: Union[List[PIReferencingMethod], PIReferencingMethod]
    ):
        """
        Set the reference methods.

        :param value: A list of PIReferencingMethod.
        """
        if isinstance(value, PIReferencingMethod):
            value = [value] * len(self.addresses)

        for address, method in zip(self.addresses, value):
            self.serial.write(f"{address} RON 1 {method.value}\n".encode("utf-8"))
            # print(f"Set reference method for device at {address}: {method.value=}")

    def fast_reference(self, negative_limit=True):
        """
        Perform a fast reference move.

        :param address: The address of the stage.
        """
        for address in self.addresses:
            self.serial.write(f"{address} SVO 1 1\n".encode("utf-8"))
            self.serial.write(
                f"{address} {'FNL' if negative_limit else 'FPL'} 1\n".encode("utf-8")
            )

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

    def home(self, wait=False):
        """
        Move the stage to the home position (make a reference to low limit).

        :param wait: If True, wait for the stage to reach the home position.
        """
        self.fast_reference()
        if wait:
            while self.is_moving:
                time.sleep(0.1)

    def stop(self):
        """
        Stop the stage.

        :param address: The address of the stage.
        """
        for address in self.addresses:
            self.serial.write(f"{address} STP\n".encode("utf-8"))

    def error(self) -> List[PIError]:
        """
        Get the error status of the stage.

        :return: The error status of the stage.
        """
        errors = []
        for address in self.addresses:
            response = self.query("ERR", address)
            assert len(response) == 1
            errors.append(PIError(int(response[0])))
        return errors
