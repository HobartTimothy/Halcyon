"""Evidence returned by research agents."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    """Compact, immutable evidence reference safe for graph state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str
    source_type: Literal[
        "knowledge_chunk",
        "web_page",
        "skill_result",
        "user_memory",
    ]
    title: str
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)
