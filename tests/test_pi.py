import random
import time
from typing import Callable

from pystages import Vector
from pystages.pi import PI, PIReferencingMethod
from pystages.pi_errors import PIError


def test_IDN(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    idns = pi.idn()
    print("\n\t".join(["IDNs:"] + idns))
    assert len(idns) == 3

    for i, idn in enumerate(idns):
        print(f"IDN {i}:", idn)
        assert "Physik Instrumente (PI) GmbH & Co. KG" in idn


def test_get_position(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    position = pi.position
    print("Position:", position)
    assert len(position) == 3  # Replace with the expected number of axes
    assert all(
        isinstance(p, float) for p in position.data
    )  # Replace with the expected type


def test_is_moving(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    is_moving = pi.is_moving
    print("Is moving:", is_moving)
    assert isinstance(is_moving, bool)


def test_fast_reference(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    pi.fast_reference(negative_limit=False)
    print("Fast reference executed.")
    time.sleep(1)
    print(f"{pi.is_moving=}")
    while pi.is_moving:
        print(f"Waiting for fast reference to finish... ({pi.position})")
        time.sleep(0.1)
    print("Fast reference finished.")

    pi.fast_reference()
    print("Fast reference executed.")
    time.sleep(1)
    print(f"{pi.is_moving=}")
    while pi.is_moving:
        print(f"Waiting for fast reference to finish... ({pi.position})")
        time.sleep(0.1)
    print("Fast reference finished.")


def test_move_random_10_times(
    require_stage: Callable[[str], None], stage_dev: str | None
):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    pi.fast_reference()
    print("Fast referencing...")
    while pi.is_moving:
        print(f"Waiting for referencing to finish... ({pi.position})")
        time.sleep(0.1)

    init_position = pi.position.data
    for _ in range(10):
        pi.move_to(
            Vector(
                random.uniform(0, init_position[0]),
                random.uniform(0, init_position[1]),
                random.uniform(0, init_position[2]),
            )
        )
        time.sleep(1)


def test_move(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    pi.fast_reference()
    print("Fast referencing...")
    while pi.is_moving:
        print(f"Waiting for referencing to finish... ({pi.position})")
        time.sleep(0.1)
    time.sleep(1)
    position = Vector(0.0, 0.0, 6.0)
    pi.position = position
    rt = "\n\t"
    print(f"Errors:{rt}{rt.join(str(e) for e in pi.error())}")
    while pi.is_moving:
        print(f"Waiting for move to {position} to finish... ({pi.position})")
        time.sleep(0.1)
    print(f"Move to {position} finished: {pi.position}")


def test_reference_method(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    print("\n" + "\n".join(m.name for m in pi.reference_methods))


def test_set_reference_method(
    require_stage: Callable[[str], None], stage_dev: str | None
):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    pi.reference_methods = [PIReferencingMethod.POS_ALLOWED] * len(pi.addresses)
    print("Reference methods set to:", pi.reference_methods)
    assert all(m == PIReferencingMethod.POS_ALLOWED for m in pi.reference_methods)


def test_error(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    errors = pi.error()
    print("Errors:", errors)
    assert isinstance(errors, list)
    assert all(e == PIError.PI_CNTR_NO_ERROR for e in errors)


def test_multiline_query(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev or "/dev/ttyUSB0", baudrate=115200, addresses=[1, 2, 3])
    avail_param_list = pi.query("HPA")
    print("Parameters list:\n", "\n".join(avail_param_list))
