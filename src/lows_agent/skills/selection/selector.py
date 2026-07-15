from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from ..core.models import SkillSpec
from ..registry.registry import SkillRegistry


class AgentSkillPolicyNotFoundError(KeyError):
    """Raised when an agent has no declared skill policy."""


class SkillPermissionError(PermissionError):
    """Raised when an agent requests a skill outside its allowlist."""


@dataclass(frozen=True, slots=True)
class AgentSkillPolicy:
    allowed: tuple[str, ...]
    defaults: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not set(self.defaults).issubset(self.allowed):
            raise ValueError("default skills must be included in allowed skills")


class SkillSelector:
    def __init__(
        self,
        registry: SkillRegistry,
        policies: Mapping[str, AgentSkillPolicy],
    ) -> None:
        self._registry = registry
        self._policies = dict(policies)

    def discover(self, agent_name: str) -> tuple[SkillSpec, ...]:
        policy = self._policy(agent_name)
        return tuple(self._registry.resolve(name) for name in policy.allowed)

    def select(
        self,
        agent_name: str,
        *,
        requested: Iterable[str] | None = None,
    ) -> tuple[SkillSpec, ...]:
        policy = self._policy(agent_name)
        names = tuple(requested) if requested is not None else policy.defaults
        denied = tuple(name for name in names if name not in policy.allowed)
        if denied:
            raise SkillPermissionError(
                f"agent {agent_name!r} cannot load skills: {', '.join(denied)}"
            )
        return tuple(self._registry.resolve(name) for name in names)

    def _policy(self, agent_name: str) -> AgentSkillPolicy:
        try:
            return self._policies[agent_name]
        except KeyError as exc:
            raise AgentSkillPolicyNotFoundError(
                f"agent has no skill policy: {agent_name}"
            ) from exc


def build_default_skill_selector(registry: SkillRegistry) -> SkillSelector:
    return SkillSelector(
        registry,
        {
            "legal_search_agent": AgentSkillPolicy(
                allowed=("legal-research",),
                defaults=("legal-research",),
            )
        },
    )
