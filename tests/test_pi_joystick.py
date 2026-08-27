from __future__ import annotations

from typing import Any

import pytest

from pystages.exceptions import ProtocolError
from pystages.pi import PI, PIVelocityLimits


class FakeSerial:
    """Minimal replacement for ``serial.Serial`` recording written commands."""

    def __init__(self) -> None:
        self.written: list[str] = []
        self.lines: list[bytes] = []

    def write(self, data: bytes) -> int:
        self.written.append(data.decode("utf-8"))
        return len(data)

    def readline(self) -> bytes:
        return self.lines.pop(0) if self.lines else b"\n"

    def push(self, address: int, payload: str) -> None:
        self.lines.append(f"0 {address} {payload}\n".encode("utf-8"))


@pytest.fixture
def fake_serial() -> FakeSerial:
    return FakeSerial()


@pytest.fixture
def pi(monkeypatch: pytest.MonkeyPatch, fake_serial: FakeSerial) -> PI:
    def fake_serial_ctor(*args: Any, **kwargs: Any) -> FakeSerial:
        _ = args, kwargs
        return fake_serial

    monkeypatch.setattr("pystages.pi.serial.Serial", fake_serial_ctor)
    for address in (1, 2, 3):
        fake_serial.push(address, "Physik Instrumente (PI) GmbH & Co. KG")
    stage = PI(dev="/dev/null", addresses=[1, 2, 3])
    fake_serial.written.clear()
    return stage


def test_enable_joystick_assigns_axis_then_enables(
    pi: PI, fake_serial: FakeSerial
) -> None:
    pi.enable_joystick()
    assert fake_serial.written == [
        "1 JAX 1 1 1\n",
        "1 JON 1 1\n",
        "2 JAX 1 1 1\n",
        "2 JON 1 1\n",
        "3 JAX 1 1 1\n",
        "3 JON 1 1\n",
    ]


def test_disable_joystick(pi: PI, fake_serial: FakeSerial) -> None:
    pi.disable_joystick()
    assert fake_serial.written == ["1 JON 1 0\n", "2 JON 1 0\n", "3 JON 1 0\n"]


def test_joystick_enabled(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1=1")
    fake_serial.push(2, "1=0")
    fake_serial.push(3, "1=1")
    assert pi.joystick_enabled == [True, False, True]
    assert fake_serial.written == ["1 JON? 1\n", "2 JON? 1\n", "3 JON? 1\n"]


def test_joystick_buttons(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1 1=0")
    fake_serial.push(2, "1 1=1")
    fake_serial.push(3, "1 1=0")
    assert pi.joystick_buttons == [False, True, False]
    assert fake_serial.written == ["1 JBS? 1 1\n", "2 JBS? 1 1\n", "3 JBS? 1 1\n"]


def test_joystick_enabled_rejects_unexpected_response(
    pi: PI, fake_serial: FakeSerial
) -> None:
    fake_serial.push(1, "oops")
    with pytest.raises(ProtocolError):
        _ = pi.joystick_enabled


def test_joystick_buttons_rejects_unexpected_response(
    pi: PI, fake_serial: FakeSerial
) -> None:
    fake_serial.push(1, "1 1=2")
    with pytest.raises(ProtocolError):
        _ = pi.joystick_buttons


def test_joystick_direction_inverted(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1 0x61=0")
    fake_serial.push(2, "1 0x61=1")
    fake_serial.push(3, "1 0x61=0")
    assert pi.joystick_direction_inverted == [False, True, False]
    assert fake_serial.written == [
        "1 SPA? 1 0x61\n",
        "2 SPA? 1 0x61\n",
        "3 SPA? 1 0x61\n",
    ]


def test_set_joystick_direction_inverted_scalar(
    pi: PI, fake_serial: FakeSerial
) -> None:
    pi.joystick_direction_inverted = True
    assert fake_serial.written == [
        "1 SPA 1 0x61 1\n",
        "2 SPA 1 0x61 1\n",
        "3 SPA 1 0x61 1\n",
    ]


def test_set_joystick_direction_inverted_per_address(
    pi: PI, fake_serial: FakeSerial
) -> None:
    pi.joystick_direction_inverted = [False, True, False]
    assert fake_serial.written == [
        "1 SPA 1 0x61 0\n",
        "2 SPA 1 0x61 1\n",
        "3 SPA 1 0x61 0\n",
    ]


def test_get_velocity(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1=5.000000")
    fake_serial.push(2, "1=7.500000")
    fake_serial.push(3, "1=10.000000")
    assert pi.velocity == [5.0, 7.5, 10.0]
    assert fake_serial.written == ["1 VEL?\n", "2 VEL?\n", "3 VEL?\n"]


def test_get_velocity_rejects_unexpected_response(
    pi: PI, fake_serial: FakeSerial
) -> None:
    fake_serial.push(1, "oops")
    with pytest.raises(ProtocolError):
        _ = pi.velocity


def test_set_velocity_scalar_applies_to_every_axis(
    pi: PI, fake_serial: FakeSerial
) -> None:
    pi.velocity = 2.5
    assert fake_serial.written == ["1 VEL 1 2.5\n", "2 VEL 1 2.5\n", "3 VEL 1 2.5\n"]


def test_set_velocity_per_address(pi: PI, fake_serial: FakeSerial) -> None:
    pi.velocity = [1.0, 2.0, 3.0]
    assert fake_serial.written == ["1 VEL 1 1.0\n", "2 VEL 1 2.0\n", "3 VEL 1 3.0\n"]


def test_velocity_limits(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1 0x49=5.000000")
    fake_serial.push(1, "1 0xA=20.000000")
    fake_serial.push(1, "1 0xA=20.000000")
    fake_serial.push(2, "1 0x49=6.500000")
    fake_serial.push(2, "1 0xA=25.000000")
    fake_serial.push(2, "1 0xA=25.000000")
    fake_serial.push(3, "1 0x49=7.000000")
    fake_serial.push(3, "1 0xA=30.000000")
    fake_serial.push(3, "1 0xA=100.000000")
    assert pi.velocity_limits == [
        PIVelocityLimits(5.0, 20.0),
        PIVelocityLimits(6.5, 25.0),
        PIVelocityLimits(7.0, 100.0),
    ]
    assert fake_serial.written == [
        "1 SEP? 1 0x49\n",
        "1 SPA? 1 0xA\n",
        "1 SEP? 1 0xA\n",
        "2 SEP? 1 0x49\n",
        "2 SPA? 1 0xA\n",
        "2 SEP? 1 0xA\n",
        "3 SEP? 1 0x49\n",
        "3 SPA? 1 0xA\n",
        "3 SEP? 1 0xA\n",
    ]


def test_velocity_default_and_max(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1 0x49=5.000000")
    fake_serial.push(2, "1 0x49=6.500000")
    fake_serial.push(3, "1 0x49=7.000000")
    assert pi.velocity_default == [5.0, 6.5, 7.0]

    fake_serial.written.clear()
    fake_serial.push(1, "1 0xA=20.000000")
    fake_serial.push(1, "1 0xA=20.000000")
    fake_serial.push(2, "1 0xA=25.000000")
    fake_serial.push(2, "1 0xA=25.000000")
    fake_serial.push(3, "1 0xA=30.000000")
    fake_serial.push(3, "1 0xA=100.000000")
    assert pi.velocity_max == [20.0, 25.0, 100.0]


def test_velocity_limits_rejects_unexpected_response(
    pi: PI, fake_serial: FakeSerial
) -> None:
    fake_serial.push(1, "oops")
    with pytest.raises(ProtocolError):
        _ = pi.velocity_limits


def test_get_acceleration(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1=20.000000")
    fake_serial.push(2, "1=20.000000")
    fake_serial.push(3, "1=20.000000")
    assert pi.acceleration == [20.0, 20.0, 20.0]
    assert fake_serial.written == ["1 ACC?\n", "2 ACC?\n", "3 ACC?\n"]


def test_set_acceleration_scalar_applies_to_every_axis(
    pi: PI, fake_serial: FakeSerial
) -> None:
    pi.acceleration = 5.0
    assert fake_serial.written == ["1 ACC 1 5.0\n", "2 ACC 1 5.0\n", "3 ACC 1 5.0\n"]


def test_get_deceleration(pi: PI, fake_serial: FakeSerial) -> None:
    fake_serial.push(1, "1=20.000000")
    fake_serial.push(2, "1=20.000000")
    fake_serial.push(3, "1=20.000000")
    assert pi.deceleration == [20.0, 20.0, 20.0]
    assert fake_serial.written == ["1 DEC?\n", "2 DEC?\n", "3 DEC?\n"]


def test_set_deceleration_scalar_applies_to_every_axis(
    pi: PI, fake_serial: FakeSerial
) -> None:
    pi.deceleration = 5.0
    assert fake_serial.written == ["1 DEC 1 5.0\n", "2 DEC 1 5.0\n", "3 DEC 1 5.0\n"]
