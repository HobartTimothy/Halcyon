from functools import lru_cache

from .core.loader import PackageSkillLoader
from .core.runtime import SkillRuntime
from .registry.registry import build_default_skill_registry
from .selection.selector import build_default_skill_selector


@lru_cache(maxsize=1)
def get_default_skill_runtime() -> SkillRuntime:
    loader = PackageSkillLoader()
    registry = build_default_skill_registry(loader)
    selector = build_default_skill_selector(registry)
    return SkillRuntime(registry=registry, selector=selector)


__all__ = ["get_default_skill_runtime"]
