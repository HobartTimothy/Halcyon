from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from pathlib import PurePosixPath
from types import MappingProxyType

from .models import LoadedSkill, SkillSpec


class SkillLoadError(RuntimeError):
    """Base error for invalid or unavailable packaged skills."""


class UnsafeSkillPathError(SkillLoadError):
    """Raised when a declared resource escapes its skill package."""


class SkillMetadataError(SkillLoadError):
    """Raised when SKILL.md metadata conflicts with the registry."""


def _safe_resource_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise UnsafeSkillPathError(f"unsafe skill resource path: {value}")
    return path


@lru_cache(maxsize=128)
def _read_package_text(package: str, relative_path: str) -> str:
    path = _safe_resource_path(relative_path)
    try:
        resource = files(package).joinpath(*path.parts)
        if not resource.is_file():
            raise SkillLoadError(
                f"skill resource not found: {package}:{relative_path}"
            )
        return resource.read_text(encoding="utf-8")
    except SkillLoadError:
        raise
    except (ModuleNotFoundError, OSError, TypeError) as exc:
        raise SkillLoadError(
            f"cannot read skill resource: {package}:{relative_path}"
        ) from exc


def _parse_skill_document(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise SkillMetadataError("SKILL.md must start with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise SkillMetadataError("SKILL.md has invalid YAML frontmatter")

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise SkillMetadataError(f"invalid frontmatter line: {line}")
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, parts[2].strip()


class PackageSkillLoader:
    """Load validated skill instructions from importable Python packages."""

    def load(self, spec: SkillSpec) -> LoadedSkill:
        instruction_path = str(_safe_resource_path(spec.instruction_file))
        metadata, instructions = _parse_skill_document(
            _read_package_text(spec.package, instruction_path)
        )
        if metadata.get("name") != spec.name:
            raise SkillMetadataError(
                f"registered skill name {spec.name!r} does not match "
                f"SKILL.md name {metadata.get('name')!r}"
            )
        if len(instructions) < spec.min_instruction_chars:
            raise SkillMetadataError(
                f"skill {spec.name!r} instructions are unexpectedly short"
            )

        references = {
            str(_safe_resource_path(path)): _read_package_text(spec.package, path)
            for path in spec.references
        }
        return LoadedSkill(
            spec=spec,
            instructions=instructions,
            references=MappingProxyType(references),
        )
