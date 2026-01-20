import pytest

from pystages.autofocus import Autofocus


def test_autofocus_init():
    af = Autofocus()
    assert len(af) == 0


def test_autofocus_clear():
    af = Autofocus()
    af.register(1, 2, 3)
    assert len(af) == 1
    af.clear()
    assert len(af) == 0


def test_autofocus_focus():
    af = Autofocus()
    with pytest.raises(RuntimeError):
        af.focus(3, 3)
    af.register(2, 2, 10)
    with pytest.raises(RuntimeError):
        af.focus(3, 3)
    af.register(2, 3, 11)
    with pytest.raises(RuntimeError):
        af.focus(3, 3)
    af.register(3, 2, 11)
    assert af.focus(3, 3) == 12
