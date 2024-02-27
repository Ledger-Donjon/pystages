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
# Copyright 2018-2022 Ledger SAS,
# written by Olivier Hériveaux, Manuel San Pedro and Michaël Mouchous


import serial.serialutil
import time
from .vector import Vector
from .exceptions import ProtocolError, ConnectionFailure
from enum import Enum, Flag
from typing import Optional, List, Union
from .stage import Stage


class Link:
    """
    Class to control Newport SMC100 controllers. This uses a serial device to
    communicate with multiple controllers which may be configured in daisy-chain
    configuration.

    Current design allows multiple instance of SMC100 to share the same
    communication channel without being considered as the same stage. For
    example, we can have two XY stages using four SMC100 controllers connected
    in daisy-chain configuration.

    As specified in SMC100 controllers documentation, the address of the first
    controller in the daisy chain is always zero.
    """

    def __init__(self, dev: Optional[str] = None):
        """
        :param dev: Serial device. For instance `'/dev/ttyUSB0'`.
            If not provided, a suitable device is searched according to
            according to vendor and product IDs
        """
        try:
            self.serial = serial.Serial(port=dev, baudrate=57600, xonxoff=True)
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e

    def send(self, address: Optional[int], command: str):
        """
        Send a command to a controller.

        :param address: Controller address. If None, only the command is sent without prefix.
        :param command: Command string. Don't include address nor CR LF since
            they are added automatically by this method.
        """
        to_send = f'{"" if address is None else address}{command}\r\n'
        self.serial.write(to_send.encode())

    def receive(self) -> Optional[str]:
        """
        Read input serial buffer to get a response. Blocks until a response is
        available.

        :return: Received response string, CR-LF removed.
        """
        # Read at least 2 bytes for CR-LF.
        response = ""
        while True:
            # Communication contains only ASCII characters, for robustness, HSBit is masked
            c = self.serial.read(1)[0] & 0x7F
            if c == ord("\n"):
                return response
            # We may receive null characters after controller reset. Just
            # ignore it, and we will be fine, they are useless anyway.
            elif c not in (ord("\r"), 0):
                response += chr(c)

    def query(
        self, address: Optional[int], command: str, lazy_res: bool = False
    ) -> Optional[str]:
        """
        Send a query.

        :param address: Controller address. int.
        :param command: Command string, without '?'.
        :param lazy_res: If True, response is not fetched. The caller must
            ensure the response will be fetched later. This flag can be used
            for optimization to send a batch of queries and then fetch all the
            response.
        :return: Received response, or None if lazy_res is True.
        """
        self.send(address, command + "?")
        if not lazy_res:
            try:
                return self.response(address, command)
            except ProtocolError:
                # Retry to send the query
                return self.query(address, command, lazy_res)

    def response(self, address: Optional[int], command: str) -> str:
        """
        Get and return the response of a query. Parameters are required to
        check the header of the response.

        :param address: Controller address. int.
        :param command: Command string, without '?'.
        """
        query_string = f'{"" if address is None else address}{command}'
        res = self.receive()
        if res is None or res[: len(query_string)] != query_string:
            raise ProtocolError(query_string, res)
        return res[len(query_string) :]


class State(int, Enum):
    """
    Possible controller states.
    The values in this enumeration corresponds to the values returned by the
    controller.
    """

    NOT_REFERENCED_FROM_RESET = 0x0A
    NOT_REFERENCED_FROM_HOMING = 0x0B
    NOT_REFERENCED_FROM_CONFIGURATION = 0x0C
    NOT_REFERENCED_FROM_DISABLE = 0x0D
    NOT_REFERENCED_FROM_READY = 0x0E
    NOT_REFERENCED_FROM_MOVING = 0x0F
    NOT_REFERENCED_STAGE_ERROR = 0x10
    NOT_REFERENCED_FROM_JOGGING = 0x11
    CONFIGURATION = 0x14
    HOMING_RS232 = 0x1E
    HOMING_SMCRC = 0x1F
    MOVING = 0x28
    READY_FROM_HOMING = 0x32
    READY_FROM_MOVING = 0x33
    READY_FROM_DISABLE = 0x34
    READY_FROM_JOGGING = 0x35
    DISABLE_FROM_READY = 0x3C
    DISABLE_FROM_MOVING = 0x3D
    DISABLE_FROM_JOGGING = 0x3E
    JOGGING_FROM_READY = 0x46
    JOGGING_FROM_DISABLE = 0x47


class Error(int, Flag):
    """
    Information returned when querying positioner error.
    """

    OUTPUT_POWER_EXCEEDED = 1 << 9
    DC_VOLTAGE_TOO_LOW = 1 << 8
    WRONG_STAGE = 1 << 7
    HOMING_TIMEOUT = 1 << 6
    FOLLOWING_ERROR = 1 << 5
    SHORT_CIRCUIT = 1 << 4
    RMS_CURRENT_LIMIT = 1 << 3
    PEAK_CURRENT_LIMIT = 1 << 2
    POSITIVE_END_OF_RUN = 1 << 1
    NEGATIVE_END_OF_RUN = 1 << 0
    NO_ERROR = 0


class ErrorAndState:
    """
    Information returned when querying positioner error and controller state.
    """

    state = State.NOT_REFERENCED_FROM_RESET
    error = Error.NO_ERROR

    @property
    def is_referenced(self) -> bool:
        """
        :return: True if state is not one of the NOT_REFERENCED_x states.
        """
        if self.state is None:
            raise RuntimeError("state not available")
        else:
            return not (
                (self.state >= State.NOT_REFERENCED_FROM_RESET)
                and (self.state <= State.NOT_REFERENCED_FROM_JOGGING)
            )

    @property
    def is_ready(self) -> bool:
        """:return: True if state is one of READY_x states."""
        return (self.state >= State.READY_FROM_HOMING) and (
            self.state <= State.READY_FROM_JOGGING
        )

    @property
    def is_moving(self) -> bool:
        """:return: True if state is MOVING."""
        return self.state == State.MOVING

    @property
    def is_homing(self) -> bool:
        """:return: True if state is one of HOMING_x states."""
        return (self.state >= State.HOMING_RS232) and (self.state <= State.HOMING_SMCRC)

    @property
    def is_jogging(self) -> bool:
        """:return: True if state is one of JOGGING_x states."""
        return (self.state >= State.JOGGING_FROM_READY) and (
            self.state <= State.JOGGING_FROM_DISABLE
        )

    @property
    def is_disabled(self) -> bool:
        """:return: True if state is one of DISABLE_x states."""
        return (self.state >= State.DISABLE_FROM_READY) and (
            self.state <= State.DISABLE_FROM_JOGGING
        )


class SMC100(Stage):
    """
    Class to command Newport SMC100 controllers.
    """

    def __init__(self, dev: Optional[Union[str, Link, "SMC100"]], addresses: List[int]):
        """
        :param dev: Serial device string (for instance `'/dev/ttyUSB0'` or
            'COM0'), an instance of Link, or an instance of SMC100 sharing
            the same serial device.
            If not provided, a suitable device is searched according to
            according to vendor and product IDs
        :param addresses: An iterable of int controller addresses.
        """
        super().__init__(num_axis=len(addresses))
        if isinstance(dev, Link):
            self.link = dev
        elif isinstance(dev, SMC100):
            self.link = dev.link
        else:
            self.link = Link(dev)
        self.addresses = addresses
        # Hack: sometimes the controllers may be in error stage when
        # initialized (for instance if the stage is not the same as the
        # memorized one).
        # Errors prevent any command being executed. Reading the controller
        # state at startup returns and clear error flags.
        for addr in self.addresses:
            self.link.query(addr, "TS")

    @property
    def position(self):
        """
        Stage position, in micrometers.

        :getter: Query and return current stage position.
        :setter: Move stage.
        """
        result = Vector(dim=self.num_axis)
        # It is faster to send all the request and then get all the responses.
        # This reduces a lot the latency.
        for i, addr in enumerate(self.addresses):
            res = self.link.query(addr, "TP", lazy_res=False)
            if res is None:
                raise ProtocolError("TP")
            val = float(res)
            result[i] = val
        return result

    @position.setter
    def position(self, value: Vector):
        # To check dimension and range of the given value
        pos_setter = Stage.position.fset
        assert pos_setter is not None
        pos_setter(self, value)

        # Enable the motors
        self.is_disabled = False
        commands = []
        for position, addr in zip(value.data, self.addresses):
            commands.append(f"{addr}PA{position:.5f}")
        self.link.send(None, "\r\n".join(commands))

    def home(self, wait=False):
        """
        Perform home search.

        :param wait: Optionally waits for move operation to be done.
        """
        self.home_search()
        if wait:
            self.wait_move_finished()

    def home_search(self):
        """
        Perform home search.
        Home search is performed even if the axes are already referenced.
        It may be better to use home_search_if_required.
        """
        for addr in self.addresses:
            # It has been observed that OR may be not effective if another command (like TS?) is not
            # performed before
            self.get_error_and_state(addr=addr)
            self.link.send(addr, "OR")

    def home_search_if_required(self):
        """
        Perform home search for all axes which are not referenced.
        """
        for addr in self.addresses:
            state = self.get_error_and_state(addr=addr)
            if not state.is_referenced:
                self.link.send(addr, "OR")

    def get_error_and_state(self, addr: int):
        """
        Query current motion controller errors and state.
        Querying the error and state may clear error flags.

        :param addr: Address of the axis.
        :return: Current error and state, in a ErrorAndState instance.
        """
        res = self.link.query(addr, "TS")
        if res is None or len(res) != 6:
            raise ProtocolError("TS", res)
        result = ErrorAndState()
        result.error = Error(int(res[:4], 16))
        result.state = State(int(res[4:], 16))
        return result

    def enter_configuration_state(self, addr: int):
        """Enter configuration state."""
        self.link.send(addr, "PW1")

    def leave_configuration_state(self, addr):
        """
        Leave configuration state. If defined parameters are valid, the
        controller saves them in the flash memory.
        """
        self.link.send(addr, "PW0")

    def controller_address(self, addr: int):
        """
        Get controller's RS-485 address. int in [2, 31].
        """
        res = self.link.query(addr, "SA")
        if res is None:
            raise ProtocolError("SA")
        return int(res)

    def set_controller_address(self, addr: int, value: int):
        """
        Set controller's RS-485 address. int in [2, 31].
        Changing the address is only possible when the controller is in
        configuration state.
        """
        if value not in range(2, 32):
            raise ValueError("Invalid controller address")
        self.link.send(addr, f"SA{value}")

    def move_relative(self, addr: int, offset: float):
        """
        Moves relatively an axis from a given offset

        :param addr: addr of axis to move
        :param offset: offset value
        """
        # Enable the motors
        self.is_disabled = False
        self.link.send(addr, f"PR{offset:.5f}")

    def stop(self, addr: Optional[int] = None):
        """
        Stops the motion on an axis. On all axis if addr not specified.

        :param addr: Address of the axis to stop. If None, stop all the controllers
        """
        self.link.send(addr, "ST")

    def reset(self, addr: Optional[int] = None):
        """
        Resets the controller at specified address. For all controllers if not specified

        :param addr: address of the controller to reset
        """
        for addr in self.addresses if addr is None else [addr]:
            self.link.send(addr, "RS")

    def set_position(self, addr: int, value: float, blocking=True):
        """
        Sets the position of a single axis

        :param addr: address of the axis to set the position
        :param value: stage position, in micrometers
        :param blocking: if True, blocking mode: wait for the position to be
            reached before exit.
        """
        # Enable the motors
        self.is_disabled = False
        self.link.send(addr, f"PA{value:.5f}")

        if blocking:
            error_and_state = self.get_error_and_state(addr=addr)
            while error_and_state.is_moving:
                time.sleep(0.1)

    @property
    def is_moving(self) -> bool:
        """
        Indicates if the stage is currently moving due to MOVE, HOME or JOG operation.

        :return: Moving state of the stage
        """
        for addr in self.addresses:
            state = self.get_error_and_state(addr=addr)
            if state.is_moving or state.is_homing or state.is_jogging:
                return True
        return False

    @property
    def is_disabled(self) -> bool:
        """
        Indicates if the stage is currently in DISABLE state.
        :return: Disabled state of the stage
        """
        for addr in self.addresses:
            state = self.get_error_and_state(addr=addr)
            if state.is_disabled:
                return True
        return False

    @is_disabled.setter
    def is_disabled(self, value: bool):
        # self.is_disabled = True makes enter DISABLE state
        self.enter_leave_disable_state(None, enter=value)

    def enter_leave_disable_state(self, addr: Optional[int], enter: bool = True):
        """
        Permits for a specified axis to enter or leave the DISABLE state.
        DISABLE state makes the motor not energized and opens the control loop.

        :param addr: address of the axis to operate.
            If None is passed, it applies to all controllers
        :param enter: True to enter, False to leave DISABLE state
        """
        # MM0 changes the controller’s state from READY to DISABLE (enter)
        # MM1 changes the controller’s state from DISABLE to READY (leave)
        self.link.send(addr, f"MM{0 if enter else 1}")
