import random
import time
from typing import Callable
import logging
from pystages import Vector
from pystages.pi import PI, PIReferencingMethod
from pystages.pi_errors import PIError

logger = logging.getLogger("PI")
logger.addHandler(logging.StreamHandler())


def test_IDN(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    init_idns = pi.__getattribute__("_idns")
    pi.logger.info("IDNs obtained from __init__ function:")
    assert len(init_idns) == len(pi.addresses)
    for i, idn in enumerate(init_idns):
        pi.logger.info(f"{i}. IDN: %s", idn)
        assert "Physik Instrumente (PI) GmbH & Co. KG" in idn

    pi.logger.info("IDNs from 'IDN?' query:")
    idns = pi.idn()
    pi.logger.info("\n\t".join(["IDNs:"] + idns))
    assert len(idns) == len(pi.addresses)

    for i, idn in enumerate(idns):
        pi.logger.info(f"{i}. IDN: %s", idn)
        assert "Physik Instrumente (PI) GmbH & Co. KG" in idn


def test_get_position(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    position = pi.position
    pi.logger.info("Position: %s", position)
    assert len(position) == 3  # Replace with the expected number of axes
    assert all(
        isinstance(p, float) for p in position.data
    )  # Replace with the expected type


def test_is_moving(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    is_moving = pi.is_moving
    pi.logger.info("Is moving: %s", is_moving)
    assert isinstance(is_moving, bool)
    pi.home()
    while pi.is_moving:
        pi.logger.info(f"Waiting for home to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Home finished.")
    pi.logger.info("Planning a move in X-direction...")
    pi.move_to(Vector(10.0, 0.0, 0.0), wait=False)
    while pi.is_moving:
        pi.logger.info(f"Waiting for move to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Move finished.")
    pi.logger.info("Planning a move in Y-direction...")
    pi.move_to(Vector(10.0, 10.0, 0.0), wait=False)
    while pi.is_moving:
        pi.logger.info(f"Waiting for move to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Move finished.")
    pi.logger.info("Planning a move in Z-direction...")
    pi.move_to(Vector(10.0, 10.0, 10.0), wait=False)
    while pi.is_moving:
        pi.logger.info(f"Waiting for move to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Homeing...")
    pi.home(wait=True)
    pi.logger.info("Home finished.")


def test_fast_reference(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    pi.logger.info("Fast referencing to positive limit...")
    pi.fast_reference(negative_limit=False)
    time.sleep(1)
    pi.logger.info(f"{pi.is_moving=}")
    while pi.is_moving:
        pi.logger.info(f"Waiting for fast reference to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Fast reference finished.")

    pi.logger.info("Fast referencing to negative limit...")
    pi.fast_reference()
    pi.logger.info(f"{pi.is_moving=}")
    while pi.is_moving:
        pi.logger.info(f"Waiting for fast reference to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Fast reference finished.")


def test_move_random_10_times(
    require_stage: Callable[[str], None], stage_dev: str | None
):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    pi.logger.info("Fast referencing to positive limit...")
    pi.fast_reference(negative_limit=False)
    while pi.is_moving:
        pi.logger.info(f"Waiting for referencing to finish... ({pi.position})")
        time.sleep(0.1)
    pi.logger.info("Referencing finished.")
    init_position = pi.position.data
    pi.logger.info("Initial position: %s", init_position)
    for _ in range(10):
        new_position = Vector(
            random.uniform(0, init_position[0]),
            random.uniform(0, init_position[1]),
            random.uniform(0, init_position[2]),
        )
        pi.logger.info("Planning a move to: %s", new_position)
        pi.move_to(new_position)
    pi.logger.info("Homeing...")
    pi.home(wait=True)
    pi.logger.info("Home finished.")


def test_get_reference_method(
    require_stage: Callable[[str], None], stage_dev: str | None
):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    pi.logger.info("\n" + "\n".join(m.name for m in pi.reference_methods))


def test_set_reference_method(
    require_stage: Callable[[str], None], stage_dev: str | None
):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    pi.reference_methods = [PIReferencingMethod.POS_ALLOWED] * len(pi.addresses)
    pi.logger.info("Reference methods set to: %s", pi.reference_methods)
    assert all(m == PIReferencingMethod.POS_ALLOWED for m in pi.reference_methods)


def test_error(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    errors = pi.error()
    pi.logger.info("Errors: %s", errors)
    assert isinstance(errors, list)
    assert all(e == PIError.PI_CNTR_NO_ERROR for e in errors)


def test_multiline_query(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("PI")
    pi = PI(dev=stage_dev, addresses=[1, 2, 3])
    avail_param_list = pi.query("HPA")
    pi.logger.info("Parameters list:\n%s", "\n".join(avail_param_list))
    avail_param_list = pi.query("HPA", address=2)
    pi.logger.info(
        "Parameters list for Target address 2:\n%s", "\n".join(avail_param_list)
    )
    avail_param_list = pi.query("HPA", address=3)
    pi.logger.info(
        "Parameters list for Target address 3:\n%s", "\n".join(avail_param_list)
    )
