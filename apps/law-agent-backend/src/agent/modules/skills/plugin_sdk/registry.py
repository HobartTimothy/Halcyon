"""Deterministic registry for code-defined Skills."""

from typing import Any

from agent.modules.skills.plugin_sdk.base import BaseSkill


class DuplicateSkillError(ValueError):
    """Raised when the same Skill version is registered twice."""


class SkillNotFoundError(LookupError):
    """Raised when an exact Skill version is unavailable."""


SkillType = type[BaseSkill[Any, Any]]


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[tuple[str, str], SkillType] = {}

    def register(self, skill_type: SkillType) -> None:
        key = (skill_type.manifest.skill_id, skill_type.manifest.version)
        if key in self._skills:
            raise DuplicateSkillError(f"duplicate skill version: {key[0]}@{key[1]}")
        self._skills[key] = skill_type

    def resolve(self, skill_id: str, version: str) -> SkillType:
        try:
            return self._skills[(skill_id, version)]
        except KeyError as exc:
            raise SkillNotFoundError(f"unknown skill version: {skill_id}@{version}") from exc

    def snapshot(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self._skills))
