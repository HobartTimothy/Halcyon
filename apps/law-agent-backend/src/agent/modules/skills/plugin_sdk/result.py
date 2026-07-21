"""Typed Skill execution result."""

from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

OutputT = TypeVar("OutputT", bound=BaseModel)


class SkillResultStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class SkillResult(BaseModel, Generic[OutputT]):
    model_config = ConfigDict(extra="forbid")

    status: SkillResultStatus
    data: OutputT | None = None
    error_code: str | None = None

    @classmethod
    def succeeded(cls, data: OutputT) -> "SkillResult[OutputT]":
        return cls(status=SkillResultStatus.SUCCEEDED, data=data)
