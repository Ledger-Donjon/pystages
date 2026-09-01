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
from enum import Enum
from typing import NamedTuple, cast
from .exceptions import ConnectionFailure, ProtocolError
from .vector import Vector
from .stage import Stage
from .pi_errors import PIError

PI_CLOSED_LOOP_VELOCITY_PARAM = 0x49
PI_MAX_CLOSED_LOOP_VELOCITY_PARAM = 0x0A
PI_MAX_CLOSED_LOOP_ACCELERATION_PARAM = 0x0B
PI_MAX_CLOSED_LOOP_DECELERATION_PARAM = 0x0C
PI_MIN_CLOSED_LOOP_VELOCITY = 0.0
PI_JOYSTICK_INVERT_DIRECTION_PARAM = 0x61

_JOYSTICK_ID = 1
_JOYSTICK_AXIS = 1
_JOYSTICK_BUTTON = 1
_JOYSTICK_CONTROLLER_AXIS = 1


class PIReferencingMethod(int, Enum):
    """
    Enum for PI reference methods.
    """

    POS_ALLOWED = 0  # An absolute position value can be assigned with POS, or a referencing move can be started with FRF, FNL or FPL.
    REFERENCING_ONLY = 1  # A referencing move must be started with FRF, FNL or FPL. Using POS is not allowed.


class PIVelocityLimits(NamedTuple):
    """
    Closed-loop velocity bounds for one controller axis.

    * ``minimum`` is always ``0`` (slowest ``VEL`` setting).
    * ``default`` comes from non-volatile memory (parameter 0x49, ``SEP?``):
      the value loaded at power-up.
    * ``maximum`` is the upper bound for ``VEL`` (parameter 0xA): the higher
      value returned by ``SPA?`` (volatile) and ``SEP?`` (non-volatile).
    """

    default: float
    maximum: float

    @property
    def minimum(self) -> float:
        return PI_MIN_CLOSED_LOOP_VELOCITY


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
        try:
            sender_address = int(response_list[0].strip())
            target_address = int(response_list[1].strip())
        except ValueError:
            raise ProtocolError(
                query=f"{address} #{command}",
                response=response,
                expected="Sender's or target's address formatted as an integer",
            )
        if sender_address != 0 or target_address != address:
            raise ProtocolError(
                query=f"{address} #{command}",
                response=response,
                expected=f"Sender's address 0 and target's address {address}",
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
                if len(response) != 3:
                    raise ProtocolError(
                        query=cmd,
                        response=_response,
                        expected="3 parts in the response, separated by spaces",
                    )
                try:
                    sender_address = int(response[0].strip())
                    target_address = int(response[1].strip())
                except ValueError:
                    raise ProtocolError(
                        query=cmd,
                        response=_response,
                        expected="Sender's or target's address formatted as an integer",
                    )
                if sender_address != 0 or target_address != address:
                    raise ProtocolError(
                        query=cmd,
                        response=_response,
                        expected=f"Sender's address 0 and target's address {address}",
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
            if len(response) != 2 or int(response[0].strip()) != 1:
                raise ProtocolError(
                    query=f"{a} POS?",
                    response=res,
                    expected="2 parts in the response, separated by =, with the first part being '1'",
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
            if response[2].strip() != "0":
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
            reference_method: str = self.query("RON", address)[0].split("=")[1].strip()
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
            if not self.query("FRF", address)[0].split("=")[1].strip() == "1":
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
                error_code_int = int(response[0].strip())
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

    def _axis_values(self, command: str) -> list[float]:
        """Query a per-axis motion setting: ``VEL?``, ``ACC?`` or ``DEC?``."""
        values: list[float] = []
        for address in self.addresses:
            res = self.query(command, address)[0]
            item, separator, value = res.partition("=")
            if not separator or item.strip() != "1":
                raise ProtocolError(
                    query=f"{address} {command}?",
                    response=res,
                    expected="2 parts in the response, separated by =, with the first part being '1'",
                )
            values.append(float(value.strip()))
        return values

    def _set_axis_values(self, command: str, value: float | list[float]) -> None:
        """Set a per-axis motion setting: ``VEL``, ``ACC`` or ``DEC``."""
        if isinstance(value, (int, float)):
            value = [float(value)] * len(self.addresses)
        for address, axis_value in zip(self.addresses, value):
            self.send(address, f"{command} 1 {axis_value}")

    def _max_parameter(self, address: int, param_id: int) -> float:
        """Higher of the volatile (``SPA?``) and non-volatile (``SEP?``) limit."""
        return max(
            self._query_parameter(address, param_id, nonvolatile=False),
            self._query_parameter(address, param_id, nonvolatile=True),
        )

    @property
    def velocity(self) -> list[float]:
        """
        Closed-loop velocity (``VEL``) of each axis, in units per second.

        This is the maximum speed reached in closed-loop motion, and the
        ceiling that joystick control scales via its lookup table factor
        (-1.0 to 1.0). Lowering it is the usual fix for a joystick which
        feels too fast.

        Accepts a single value applied to every axis, or one value per
        controller address.
        """
        return self._axis_values("VEL")

    @velocity.setter
    def velocity(self, value: float | list[float]) -> None:
        self._set_axis_values("VEL", value)

    @property
    def acceleration(self) -> list[float]:
        """
        Closed-loop acceleration (``ACC``) of each axis, in units per second
        squared.

        The profile generator enforces this limit even while the axis is under
        joystick control: it bounds how fast the commanded velocity can ramp up
        towards the joystick-requested value. Lowering it smooths abrupt
        joystick movements and reduces the peak motor current, which helps
        avoid the amplifier's overcurrent protection tripping
        (``PI_CNTR_OVER_CURR_PROTEC_TRIGGERED_BY_AMP_MODULE``).

        Accepts a single value applied to every axis, or one value per
        controller address.
        """
        return self._axis_values("ACC")

    @acceleration.setter
    def acceleration(self, value: float | list[float]) -> None:
        self._set_axis_values("ACC", value)

    @property
    def deceleration(self) -> list[float]:
        """
        Closed-loop deceleration (``DEC``) of each axis, in units per second
        squared. Same rationale as :attr:`acceleration`, on the ramp-down side
        of a motion.
        """
        return self._axis_values("DEC")

    @deceleration.setter
    def deceleration(self, value: float | list[float]) -> None:
        self._set_axis_values("DEC", value)

    @property
    def velocity_limits(self) -> list[PIVelocityLimits]:
        """
        Default and maximum closed-loop velocity for each controller address.

        The default is read from non-volatile memory (parameter 0x49 via
        ``SEP?``). The maximum is parameter 0xA, queried in both volatile
        (``SPA?``) and non-volatile (``SEP?``) memory; the higher value is
        used.
        """
        return [
            PIVelocityLimits(
                self._query_parameter(
                    address, PI_CLOSED_LOOP_VELOCITY_PARAM, nonvolatile=True
                ),
                self._max_parameter(address, PI_MAX_CLOSED_LOOP_VELOCITY_PARAM),
            )
            for address in self.addresses
        ]

    @property
    def velocity_default(self) -> list[float]:
        """Default closed-loop velocity loaded at power-up (parameter 0x49)."""
        return [
            self._query_parameter(
                address, PI_CLOSED_LOOP_VELOCITY_PARAM, nonvolatile=True
            )
            for address in self.addresses
        ]

    @property
    def velocity_max(self) -> list[float]:
        """Maximum settable closed-loop velocity (parameter 0xA)."""
        return [
            self._max_parameter(address, PI_MAX_CLOSED_LOOP_VELOCITY_PARAM)
            for address in self.addresses
        ]

    @property
    def acceleration_max(self) -> list[float]:
        """Maximum settable closed-loop acceleration (parameter 0xB)."""
        return [
            self._max_parameter(address, PI_MAX_CLOSED_LOOP_ACCELERATION_PARAM)
            for address in self.addresses
        ]

    @property
    def deceleration_max(self) -> list[float]:
        """Maximum settable closed-loop deceleration (parameter 0xC)."""
        return [
            self._max_parameter(address, PI_MAX_CLOSED_LOOP_DECELERATION_PARAM)
            for address in self.addresses
        ]

    def enable_joystick(self) -> None:
        """Enable analog joystick control on every configured controller."""
        self.joystick_enabled = True

    def disable_joystick(self) -> None:
        """Disable analog joystick control on every configured controller."""
        self.joystick_enabled = False

    @property
    def joystick_enabled(self) -> list[bool]:
        """
        Activation state of joystick device 1, for each controller address.

        Enabling an axis switches it to closed-loop mode (``SVO 1 1``), which
        the joystick requires, assigns controller axis 1 to joystick device 1 /
        axis 1 (``JAX``), then enables the device (``JON``). Motion commands
        are rejected while the joystick is enabled, and enabling it with no
        device connected can cause unintentional axis motion.

        Accepts a single flag applied to every axis, or one flag per controller
        address, so that axes can be driven independently.
        """
        states: list[bool] = []
        for address in self.addresses:
            payload = self.query("JON", address, args=[str(_JOYSTICK_ID)])[0]
            states.append(
                self._parse_bool_assignment(
                    payload,
                    query=f"{address} JON? {_JOYSTICK_ID}",
                    expected_left=str(_JOYSTICK_ID),
                )
            )
        return states

    @joystick_enabled.setter
    def joystick_enabled(self, value: bool | list[bool]) -> None:
        if isinstance(value, bool):
            value = [value] * len(self.addresses)
        for address, enabled in zip(self.addresses, value):
            if enabled:
                self.send(address, "SVO 1 1")
                self.send(
                    address,
                    f"JAX {_JOYSTICK_ID} {_JOYSTICK_AXIS} {_JOYSTICK_CONTROLLER_AXIS}",
                )
            self.send(address, f"JON {_JOYSTICK_ID} {int(enabled)}")

    @property
    def joystick_buttons(self) -> list[bool]:
        """
        Pressed state of joystick button 1 for each controller address.

        On the C-863.12 there is one button per joystick device, and one
        joystick device per controller.
        """
        states: list[bool] = []
        for address in self.addresses:
            payload = self.query(
                "JBS",
                address,
                args=[str(_JOYSTICK_ID), str(_JOYSTICK_BUTTON)],
            )[0]
            states.append(
                self._parse_bool_assignment(
                    payload,
                    query=f"{address} JBS? {_JOYSTICK_ID} {_JOYSTICK_BUTTON}",
                    expected_left=f"{_JOYSTICK_ID} {_JOYSTICK_BUTTON}",
                )
            )
        return states

    @property
    def joystick_direction_inverted(self) -> list[bool]:
        """
        Inversion of joystick motion direction for each controller address.

        Maps to parameter 0x61 (``SPA?`` / ``SPA``): ``0`` normal, ``1`` inverted.
        """
        return [
            self._query_parameter(address, PI_JOYSTICK_INVERT_DIRECTION_PARAM) != 0.0
            for address in self.addresses
        ]

    @joystick_direction_inverted.setter
    def joystick_direction_inverted(self, value: bool | list[bool]) -> None:
        if isinstance(value, bool):
            value = [value] * len(self.addresses)
        for address, inverted in zip(self.addresses, value):
            self.send(
                address,
                f"SPA 1 0x{PI_JOYSTICK_INVERT_DIRECTION_PARAM:X} {int(inverted)}",
            )

    def _parse_bool_assignment(
        self, payload: str, query: str, expected_left: str
    ) -> bool:
        parts = payload.split("=")
        left = parts[0].strip() if parts else ""
        right = parts[1].strip() if len(parts) == 2 else ""
        if len(parts) != 2 or left != expected_left or right not in {"0", "1"}:
            raise ProtocolError(
                query=query,
                response=payload,
                expected=f"{expected_left}=<0|1>",
            )
        return right == "1"

    def _query_parameter(
        self, address: int, param_id: int, *, nonvolatile: bool = False
    ) -> float:
        command = "SEP" if nonvolatile else "SPA"
        param = f"0x{param_id:X}"
        payload = self.query(command, address, args=["1", param])[0]
        try:
            return float(payload.rsplit("=", 1)[1].strip())
        except (IndexError, ValueError):
            raise ProtocolError(
                query=f"{address} {command}? 1 {param}",
                response=payload,
                expected="parameter assignment (<item> <id>=<value>)",
            )
