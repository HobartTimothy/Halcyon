import pytest
from pydantic import ValidationError

from agent.shared.contracts.run_events import RunEvent


def test_run_event_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        RunEvent(
            schema_version="1.0",
            event_id="1-0",
            event_type="run.started",
            run_id="run-1",
            sequence=1,
            data={},
            unknown=True,
        )


def test_run_event_rejects_negative_sequence() -> None:
    with pytest.raises(ValidationError):
        RunEvent(
            schema_version="1.0",
            event_id="1-0",
            event_type="run.started",
            run_id="run-1",
            sequence=-1,
            data={},
        )
