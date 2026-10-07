from typing import TypeVar

from pydantic import BaseModel

from agent.modules.llm.factory import get_chat_model

T = TypeVar("T", bound=BaseModel)


def get_structured_llm(
    output_schema: type[T],
    temperature: float = 0.0,
    include_raw: bool = False,
    strict: bool = True,
):
    llm = get_chat_model(temperature=temperature)

    return llm.with_structured_output(
        schema=output_schema,
        method="json_schema",
        strict=strict,
        include_raw=include_raw,
    )
