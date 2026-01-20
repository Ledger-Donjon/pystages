from collections.abc import Callable

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


@pytest.fixture
def enabled_stage(request: pytest.FixtureRequest) -> str | None:
    raw = request.config.getoption("--stage")
    if not raw:
        return None
    return raw.strip().lower()


@pytest.fixture
def require_stage(enabled_stage: str) -> Callable[[str], None]:
    def _require(stage_name: str) -> None:
        if enabled_stage != stage_name.lower():
            pytest.skip(
                f"Stage '{stage_name}' not enabled. Use --stage={stage_name}."
            )
    return _require


@pytest.fixture
def stage_dev(request: pytest.FixtureRequest) -> str | None:
    return request.config.getoption("--dev")
