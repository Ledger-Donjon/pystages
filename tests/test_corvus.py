from typing import Callable
import random
from pystages.vector import Vector
from pystages.corvus import Corvus


def test_connect(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    assert corvus.is_connected


def test_get_position(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    position = corvus.position
    corvus.logger.info(f"Position: {position}")
    assert len(position) == 3
    assert all(isinstance(p, float) for p in position)


def test_get_velocity(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    velocity = corvus.velocity
    corvus.logger.info(f"Velocity: {velocity}")
    assert isinstance(velocity, float)
    assert velocity >= 0


def test_get_acceleration(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    acceleration = corvus.acceleration
    corvus.logger.info(f"Acceleration: {acceleration}")
    assert isinstance(acceleration, float)
    assert acceleration >= 0


def test_move_relative(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    corvus.move_relative(1000, 1000, 1000)
    assert not corvus.is_moving
    corvus.logger.info(f"Position: {corvus.position}")
    corvus.move_relative(-1000, -1000, -1000)
    assert not corvus.is_moving
    corvus.logger.info(f"Position: {corvus.position}")
    corvus.enable_joystick()


def test_calibrate_xy(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    corvus.calibrate_xy()
    assert not corvus.is_moving
    corvus.logger.info(f"Position: {corvus.position}")
    corvus.enable_joystick()


def test_calibrate(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    corvus.calibrate()
    assert not corvus.is_moving
    corvus.logger.info(f"Position: {corvus.position}")
    corvus.enable_joystick()


def test_home(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    initial_position = corvus.position
    corvus.logger.info(f"Position: {initial_position}")
    corvus.home(wait=True)
    assert not corvus.is_moving
    corvus.logger.info(f"Position: {corvus.position}")
    corvus.move_to(Vector(-5914.01706, -9634.31359, -41736.88786), wait=True)
    assert not corvus.is_moving
    corvus.logger.info(f"Position: {corvus.position}")
    corvus.enable_joystick()


def test_10_random_moves(
    require_stage: Callable[[str], None], log_level: str, serial_number: str | None
):
    require_stage("Corvus")
    corvus = Corvus(serial_number=serial_number)
    corvus.calibrate()
    initial_position = corvus.position
    for _ in range(10):
        new_position = Vector(
            random.randint(0, int(initial_position.x)),
            random.randint(0, int(initial_position.y)),
            random.randint(0, int(initial_position.z)),
        )
        corvus.move_to(new_position, wait=True)
        assert not corvus.is_moving
        corvus.logger.info(f"Position: {corvus.position}")
        # assert that the position is close to the initial position
        assert abs(corvus.position.x - new_position.x) < 5  # 5 micrometers
        assert abs(corvus.position.y - new_position.y) < 5  # 5 micrometers
        assert abs(corvus.position.z - new_position.z) < 5  # 5 micrometers
    corvus.enable_joystick()
