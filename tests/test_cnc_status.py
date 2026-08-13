import logging

import pytest

from pystages.cncrouter import CNCRouter, CNCStatus
from pystages.stage import Stage


def make_router_with_status(
    monkeypatch: pytest.MonkeyPatch, response: str
) -> CNCRouter:
    router = CNCRouter.__new__(CNCRouter)
    Stage.__init__(router, num_axis=3)
    monkeypatch.setattr(router, "send", lambda *args, **kwargs: None)
    monkeypatch.setattr(router, "receive", lambda: response)
    return router


@pytest.mark.parametrize(
    ("raw_status", "expected_status"),
    [("Run,0", CNCStatus.RUN), ("Hold:0", CNCStatus.HOLD)],
)
def test_get_current_status_normalizes_substate(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    raw_status: str,
    expected_status: CNCStatus,
):
    router = make_router_with_status(
        monkeypatch,
        f"<{raw_status}|MPos:1.000,2.000,3.000|WCO:0.000,0.000,0.000>",
    )
    caplog.set_level(logging.DEBUG, logger="CNCRouter")

    result = router.get_current_status()

    assert result == (
        expected_status,
        {
            "MPos": ["1.000", "2.000", "3.000"],
            "WCO": ["0.000", "0.000", "0.000"],
        },
    )
    assert (
        f"Normalizing CNC status '{raw_status}' to '{expected_status.value}'"
        in caplog.messages
    )


def test_get_current_status_keeps_unsuffixed_status(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    router = make_router_with_status(monkeypatch, "<Idle|MPos:1.000,2.000,3.000>")
    caplog.set_level(logging.DEBUG, logger="CNCRouter")

    result = router.get_current_status()

    assert result == (
        CNCStatus.IDLE,
        {"MPos": ["1.000", "2.000", "3.000"]},
    )
    assert not caplog.messages
