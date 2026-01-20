from collections.abc import Callable

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--stages",
        action="store",
        default="",
        help="Liste de types de stages à activer (ex: pi,smc100,cnc).",
    )
    parser.addoption(
        "--dev",
        action="store",
        default=None,
        help="Chemin du device/port série à utiliser pour les tests hardware.",
    )


@pytest.fixture
def enabled_stages(request: pytest.FixtureRequest) -> set[str]:
    raw = request.config.getoption("--stages")
    if not raw:
        return set()
    return {stage.strip().lower() for stage in raw.split(",") if stage.strip()}


@pytest.fixture
def require_stage(enabled_stages: set[str]) -> Callable[[str], None]:
    def _require(stage_name: str) -> None:
        if stage_name.lower() not in enabled_stages:
            pytest.skip(
                f"Stage '{stage_name}' non activé. Utilisez --stages={stage_name}."
            )

    return _require


@pytest.fixture
def stage_dev(request: pytest.FixtureRequest) -> str | None:
    return request.config.getoption("--dev")
