from pydantic import BaseModel
from typing import Type, TypeVar, Any, Dict, Union
from lows_agent.llm.factory import get_chat_model

T = TypeVar('T', bound=BaseModel)


def get_structured_llm(output_schema: Type[T],
                       temperature: float = 0.0,
                       include_raw: bool = False,
                       strict: bool = True):
    """
    获取一个强制返回指定 Pydantic 模型的 LLM 实例。

    优化点：
    1. strict=True: 启用 OpenAI 原生的 Structured Outputs 强约束。
    2. method="json_schema": 使用比 function_calling 更严格和高效的 JSON Schema 解析层。
    3. include_raw: 允许上层业务捕获原始输出和解析错误，避免 Agent 节点直接崩溃。
    """

    llm = get_chat_model(temperature=temperature)

    return llm.with_structured_output(
        schema=output_schema,
        method="json_schema",  # 使用专用的结构化输出模式
        strict=strict,  # 保证模型输出 100% 严格匹配 Schema
        include_raw=include_raw  # 是否返回包含错误信息的字典
    )
