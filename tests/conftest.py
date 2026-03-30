from typing import Callable, cast
import logging
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--stage",
        action="store",
        default=None,
        help="Stage type(s) to enable (e.g. PI, SMC100, CNC).",
    )
    parser.addoption(
        "--dev",
        action="store",
        default=None,
        help="Device/serial port to use for hardware tests.",
    )
    parser.addoption(
        "--serial-number",
        action="store",
        default=None,
        help="Serial number of the stage to use for hardware tests.",
    )


@pytest.fixture
def enabled_stage(request: pytest.FixtureRequest) -> str | None:
    raw = cast(str | None, request.config.getoption("--stage"))
    if raw is None:
        return None
    return raw.strip().lower()


@pytest.fixture
def require_stage(enabled_stage: str | None) -> Callable[[str], None]:
    def _require(stage_name: str) -> None:
        if enabled_stage is None:
            pytest.skip("No stage specified. Use --stage=<name> to run hardware tests.")
        if enabled_stage.lower() != stage_name.lower():
            pytest.skip(f"Stage '{stage_name}' not enabled. Use --stage={stage_name}.")

    return _require


@pytest.fixture
def stage_dev(request: pytest.FixtureRequest) -> str | None:
    return cast(str | None, request.config.getoption("--dev"))


@pytest.fixture
def serial_number(request: pytest.FixtureRequest) -> str | None:
    return cast(str | None, request.config.getoption("--serial-number"))


@pytest.fixture
def log_level(request: pytest.FixtureRequest) -> str:
    level = cast(str, request.config.getoption("--log-level") or "INFO").upper()
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(level)
    return level
