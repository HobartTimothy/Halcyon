from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class RiskLevel(StrEnum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"


class SkillManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    skill_id: str
    version: str
    display_name: str
    description: str
    capabilities: frozenset[str]
    default_risk_level: RiskLevel
    side_effect: bool
    requires_approval: bool
    idempotency_required: bool

    @model_validator(mode="after")
    def validate_safety_invariants(self) -> "SkillManifest":
        if self.default_risk_level is RiskLevel.R4:
            raise ValueError("R4 skills cannot be registered")
        if self.side_effect and not self.idempotency_required:
            raise ValueError("side-effect skills must require idempotency")
        if self.default_risk_level in {RiskLevel.R2, RiskLevel.R3} and not self.requires_approval:
            raise ValueError("R2 and R3 skills must require approval")
        return self
