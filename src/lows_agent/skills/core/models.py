from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass


_SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class SkillSpec:
    name: str
    package: str
    instruction_file: str = "SKILL.md"
    references: tuple[str, ...] = ()
    min_instruction_chars: int = 100

    def __post_init__(self) -> None:
        if not _SKILL_NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f"invalid skill name: {self.name}")
        if not self.package or any(not part for part in self.package.split(".")):
            raise ValueError(f"invalid skill package: {self.package}")
        if self.min_instruction_chars < 1:
            raise ValueError("min_instruction_chars must be positive")


@dataclass(frozen=True, slots=True)
class LoadedSkill:
    spec: SkillSpec
    instructions: str
    references: Mapping[str, str]

    @property
    def name(self) -> str:
        return self.spec.name

    def render_prompt(self) -> str:
        sections = [f"# Skill: {self.name}\n\n{self.instructions.strip()}"]
        sections.extend(
            f"## Reference: {path}\n\n{content.strip()}"
            for path, content in self.references.items()
        )
        return "\n\n".join(sections)
