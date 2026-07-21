import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from agent.modules.skills.plugin_sdk.base import BaseSkill
from agent.modules.skills.plugin_sdk.manifest import RiskLevel, SkillManifest
from agent.modules.skills.plugin_sdk.registry import DuplicateSkillError, SkillRegistry
from agent.modules.skills.plugin_sdk.result import SkillResult


class EchoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str


class EchoOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str


class EchoSkill(BaseSkill[EchoInput, EchoOutput]):
    manifest = SkillManifest(
        skill_id="system.echo",
        version="1.0.0",
        display_name="Echo",
        description="Returns the supplied text.",
        capabilities=frozenset({"system.read"}),
        default_risk_level=RiskLevel.R0,
        side_effect=False,
        requires_approval=False,
        idempotency_required=False,
    )
    input_model = EchoInput
    output_model = EchoOutput

    async def execute(self, request: EchoInput) -> SkillResult[EchoOutput]:
        return SkillResult.succeeded(EchoOutput(text=request.text))


def test_registry_resolves_exact_version() -> None:
    registry = SkillRegistry()
    registry.register(EchoSkill)
    assert registry.resolve("system.echo", "1.0.0") is EchoSkill


def test_registry_rejects_duplicate_version() -> None:
    registry = SkillRegistry()
    registry.register(EchoSkill)
    with pytest.raises(DuplicateSkillError):
        registry.register(EchoSkill)


def test_r2_skill_requires_approval() -> None:
    with pytest.raises(ValidationError):
        SkillManifest(
            skill_id="mail.send",
            version="1.0.0",
            display_name="Send mail",
            description="Sends an external email.",
            capabilities=frozenset({"email.send"}),
            default_risk_level=RiskLevel.R2,
            side_effect=True,
            requires_approval=False,
            idempotency_required=True,
        )
