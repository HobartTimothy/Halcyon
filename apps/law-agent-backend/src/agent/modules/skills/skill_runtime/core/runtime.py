from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..registry.registry import SkillRegistry
from ..selection.selector import SkillSelector
from .models import LoadedSkill


@dataclass(frozen=True, slots=True)
class SkillRuntime:
    registry: SkillRegistry
    selector: SkillSelector

    def select_for_agent(
        self,
        agent_name: str,
        requested: Iterable[str] | None = None,
    ) -> tuple[LoadedSkill, ...]:
        specs = self.selector.select(agent_name, requested=requested)
        return tuple(self.registry.load(spec.name) for spec in specs)

    def render_for_agent(
        self,
        agent_name: str,
        requested: Iterable[str] | None = None,
    ) -> str:
        skills = self.select_for_agent(agent_name, requested=requested)
        if not skills:
            return ""
        return "\n\n".join(skill.render_prompt() for skill in skills)
