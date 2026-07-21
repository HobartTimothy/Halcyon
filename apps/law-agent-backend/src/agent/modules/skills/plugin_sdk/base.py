from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

from agent.modules.skills.plugin_sdk.manifest import SkillManifest
from agent.modules.skills.plugin_sdk.result import SkillResult

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseSkill(ABC, Generic[InputT, OutputT]):
    manifest: ClassVar[SkillManifest]
    input_model: ClassVar[type[BaseModel]]
    output_model: ClassVar[type[BaseModel]]

    @abstractmethod
    async def execute(self, request: InputT) -> SkillResult[OutputT]:
        """Execute a validated Skill request."""
