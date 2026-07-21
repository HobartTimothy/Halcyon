"""HTTP schemas for demo agent runs."""

from pydantic import BaseModel, ConfigDict, Field


class DemoRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=2000)


class DemoRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str
    final_answer: str
    evidence_count: int = Field(ge=0)
