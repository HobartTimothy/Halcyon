from __future__ import annotations

from collections.abc import Iterable

from ..core.loader import PackageSkillLoader
from ..core.models import LoadedSkill, SkillSpec


class DuplicateSkillError(ValueError):
    """Raised when the same skill name is registered twice."""


class SkillNotFoundError(KeyError):
    """Raised when a requested skill is not registered."""


class SkillRegistry:
    def __init__(self, loader: PackageSkillLoader) -> None:
        self._loader = loader
        self._specs: dict[str, SkillSpec] = {}

    def register(self, spec: SkillSpec) -> None:
        if spec.name in self._specs:
            raise DuplicateSkillError(f"skill already registered: {spec.name}")
        self._specs[spec.name] = spec

    def register_many(self, specs: Iterable[SkillSpec]) -> None:
        for spec in specs:
            self.register(spec)

    def resolve(self, name: str) -> SkillSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise SkillNotFoundError(f"skill is not registered: {name}") from exc

    def load(self, name: str) -> LoadedSkill:
        return self._loader.load(self.resolve(name))

    def names(self) -> tuple[str, ...]:
        return tuple(self._specs)


def build_default_skill_registry(loader: PackageSkillLoader) -> SkillRegistry:
    registry = SkillRegistry(loader)
    registry.register(
        SkillSpec(
            name="legal-research",
            package="lows_agent.skill_packages.research",
            references=("references/jurisdiction_sources.md",),
        )
    )
    return registry
