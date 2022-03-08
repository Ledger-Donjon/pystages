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
# Copyright 2018-2020 Ledger SAS,
# written by Olivier Hériveaux and Manuel San Pedro


import serial
import time
from .vector import Vector
from .exceptions import ProtocolError, ConnectionFailure
from enum import Enum


class Link:
    """
    Class to control Newport SMC100 controllers. This uses a serial device to
    communicate with multiple controllers which may be configured in daiy-chain
    configuration.

    Current design allows multiple instance of SMC100 to share the same
    communication channel without being considered as the same stage. For
    example, we can have two XY stages using four SMC100 controllers connected
    in daisy-chain configuration.

    As specified in SMC100 controllers documentation, the address of the first
    controller in the daisy chain is always zero.
    """
    def __init__(self, dev):
        """
        :param dev: Serial device. For instance '/dev/ttyUSB0' or 'COM0'.
        """
        try:
            self.serial = serial.Serial(port=dev, baudrate=57600, xonxoff=True)
        except serial.serialutil.SerialException as e:
            raise ConnectionFailure() from e

    def send(self, address, command):
        """
        Send a command to a controller.

        :param address: Controller address. If None, only the command is sent without prefix.
        :param command: Command string. Don't include address nor CR LF since
            they are added automatically by this method.
        """
        to_send = f'{"" if address is None else address}{command}\r\n'
        self.serial.write(to_send.encode())

    def receive(self):
        """
        Read input serial buffer to get a response. Blocks until a response is
        available.

        :return: Received response string, CR-LF removed.
        """
        # Read at least 2 bytes for CR-LF.
        response = ''
        while True:
            c = self.serial.read(1)[0]
            if c == ord('\n'):
                return response
            # We may receive null characters after controller reset. Just
            # ignore it and we will be fine, they are useless anyway.
            elif c not in (ord('\r'), 0):
                response += chr(c)

    def query(self, address, command, lazy_res=False):
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
        self.send(address, command + '?')
        if not lazy_res:
            return self.response(address, command)

    def response(self, address, command):
        """
        Get and return the response of a query. Parameters are required to
        check the header of the response.

        :param address: Controller address. int.
        :param command: Command string, without '?'.
        """
        query_string = f'{"" if address is None else address}{command}'
        res = self.receive()
        if res[:len(query_string)] != query_string:
            raise ProtocolError()
        return res[len(query_string):]


class State(Enum):
    """
    Possible controller states.
    The values in this enumeration corresponds to the values returned by the
    controller.
    """
    NOT_REFERENCED_FROM_RESET = 0x0a
    NOT_REFERENCED_FROM_HOMING = 0x0b
    NOT_REFERENCED_FROM_CONFIGURATION = 0x0c
    NOT_REFERENCED_FROM_DISABLE = 0x0d
    NOT_REFERENCED_FROM_READY = 0x0e
    NOT_REFERENCED_FROM_MOVING = 0x0f
    NOT_REFERENCED_STAGE_ERROR = 0x10
    NOT_REFERENCED_FROM_JOGGING = 0x11
    CONFIGURATION = 0x14
    HOMING_RS232 = 0x1e
    HOMING_SMCRC = 0x1f
    MOVING = 0x28
    READY_FROM_HOMING = 0x32
    READY_FROM_MOVING = 0x33
    READY_FROM_DISABLE = 0x34
    READY_FROM_JOGGING = 0x35
    DISABLE_FROM_READY = 0x3c
    DISABLE_FROM_MOVING = 0x3d
    DISABLE_FROM_JOGGING = 0x3e
    JOGGING_FROM_READY = 0x46
    JOGGING_FROM_DISABLE = 0x47


class ErrorAndState:
    """
    Information returned when querying positionner error and controller state.
    """
    state = None
    output_power_exceeded = None
    dc_voltage_too_low = None
    wrong_stage = None
    homing_timeout = None
    following_error = None
    short_circuit = None
    rms_current_limit = None
    peak_current_limit = None
    positive_end_of_run = None
    negative_end_of_run = None

    @property
    def is_referenced(self):
        """
        :return: True if state is not one of the NOT_REFERENCED_x states.
        """
        if self.state is None:
            raise RuntimeException('state not available')
        else:
            return not (
                (self.state.value >= State.NOT_REFERENCED_FROM_RESET.value) and
                (self.state.value <= State.NOT_REFERENCED_FROM_JOGGING.value))

    @property
    def is_ready(self):
        """ :return: True if state is one of READY_x states. """
        return (
            (self.state.value >= State.READY_FROM_HOMING.value) and
            (self.state.value <= State.READY_FROM_JOGGING.value))


class SMC100:
    """
    Class to command Newport SMC100 controllers.
    """
    def __init__(self, dev, addresses):
        """
        :param dev: Serial device string (for instance '/dev/ttyUSB0' or
            'COM0'), an instance of Link, or an instance of SMC100 sharing
            the same serial device.
        :param addresses: An iterable of int controller addresses.
        """
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
            self.link.query(addr, 'TS')

    @property
    def num_axis(self):
        """ :return: Number of axis of this stage. """
        return len(self.addresses)

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
        for addr in self.addresses:
            self.link.query(addr, 'TP', lazy_res=True)
        for i, addr in enumerate(self.addresses):
            val = float(self.link.response(addr, 'TP'))
            result[i] = val
        return result

    @position.setter
    def position(self, vec):
        if len(vec) != self.num_axis:
            raise ValueError('Invalid position vector dimension.')
        for i, addr in enumerate(self.addresses):
            self.link.send(addr, f'PA{vec[i]}')

    def reset(self):
        """ Reset stage controllers. """
        for addr in self.addresses:
            self.link.send(addr, 'RS')

    def home_search(self):
        """
        Perform home search.
        Home search is performed even if the axises are already referenced. It
        may be better to use home_search_if_required.
        """
        for addr in self.addresses:
            self.link.send(addr, 'OR')

    def home_search_if_required(self):
        """
        Perfom home search for axis which are not referenced.
        """
        for i, addr in enumerate(self.addresses):
            state = self.get_error_and_state(i)
            if not state.is_referenced:
                self.link.send(addr, 'OR')

    def get_error_and_state(self, axis):
        """
        Query current motion controller errors and state.
        Querying the error and state may clear error flags.

        :axis: Axis index.
        :return: Current error and state, in a ErrorAndState instance.
        """
        res = self.link.query(self.addresses[axis], 'TS')
        if len(res) != 6:
            raise ProtocolError()
        value = int(res[:4], 16)
        result = ErrorAndState()
        result.output_power_exceeded = bool(value & (1 << 9))
        result.dc_voltage_too_low = bool(value & (1 << 8))
        result.wrong_stage = bool(value & (1 << 7))
        result.homing_timeout = bool(value & (1 << 6))
        result.following_error = bool(value & (1 << 5))
        result.short_circuit = bool(value & (1 << 4))
        result.rms_current_limit = bool(value & (1 << 3))
        result.peak_current_limit = bool(value & (1 << 2))
        result.positive_end_of_run = bool(value & (1 << 1))
        result.negative_end_of_run = bool(value & 1)
        result.state = State(int(res[4:], 16))
        return result

    def enter_configuration_state(self, addr):
        """ Enter configuration state. """
        self.link.send(addr, 'PW1')

    def leave_configuration_state(self, addr):
        """
        Leave configuration state. If defined parameters are valid, the
        controller saves them in the flash memory.
        """
        self.link.send(addr, 'PW0')

    @property
    def controller_address(self, addr):
        """
        Controller's RS-485 address. int in [2, 31].
        Changing the address is only possible when the controller is in
        configuration state.
        """
        return int(self.link.query(addr, 'SA'))

    @controller_address.setter
    def controller_address(self, addr, value):
        if value not in range(2, 32):
            raise ValueError('Invalid controller address')
        self.link.send(addr, f'SA{value}')

    def move_relative(self, addr, offset):
        """
        Move relatively an axis from  a given offset

        :param addr: addr of axis
        :param offset:
        """
        self.link.send(addr, f'PR{offset}')

    def stop(self, addr=None):
        """
        Stop the motion on an axis. On all axs if addr not specitied.

        :param addr: address of the axis to stop
        """
        if addr is None:
            self.link.serial.write('ST\r\n'.encode())
        else:
            self.link.send(addr, 'ST')

    def set_position(self, addr, value, blocking=True):
        """
        set the position of a single axis

        :param addr: address of the axis to stop
        :param blocking: if True, blocking mode: wait for the position to be
            reached before exit.
        """
        self.link.send(addr, f'PA{value}')

        if blocking:
            while self.get_error_and_state(1).state.value == State.MOVING:
                time.sleep(0.1)

    def wait_move_finished(self):
        """
        Wait until all axis are ready.
        """
        for i in range(self.num_axis):
            while not self.get_error_and_state(i).is_ready:
                pass
