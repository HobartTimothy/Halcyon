"""Versioned contract for browser-safe run events."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RunEventType = Literal[
    "run.started",
    "stage.changed",
    "token.delta",
    "citation.added",
    "approval.required",
    "run.completed",
    "run.failed",
    "stream.snapshot",
    "stream.reset",
]


class RunEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    event_id: str
    event_type: RunEventType
    run_id: str
    sequence: int = Field(ge=0)
    data: dict[str, Any]
