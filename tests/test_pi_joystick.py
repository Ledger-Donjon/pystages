from __future__ import annotations

from typing import Any

import pytest

from pystages.exceptions import ProtocolError
from pystages.pi import PI


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
