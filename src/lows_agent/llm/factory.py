from __future__ import annotations

import math
from numbers import Real
from typing import Final
from functools import lru_cache
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from lows_agent.config.settings import clear_settings_cache, get_settings


# 限制不同 temperature 对应的模型实例数量，
# 避免调用方传入大量不同温度导致缓存无限增长。
CHAT_MODEL_CACHE_SIZE: Final[int] = 8


@lru_cache(maxsize=CHAT_MODEL_CACHE_SIZE)
def _get_chat_model_cached( temperature: float) -> ChatOpenAI:
    """
    根据温度创建并缓存 ChatOpenAI 实例。

    本函数只接受已经完成校验和规范化的温度参数。
    """
    settings = get_settings()

    return ChatOpenAI(
        temperature=temperature,
        model=settings.openapi_model,
        max_retries=settings.openai_max_retries,
        timeout=settings.openai_timeout,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings:
    """
    获取全局 Embedding 模型。

    一个应用进程中只创建一个 Embedding 客户端实例。

    Returns:
        已缓存的 OpenAIEmbeddings 实例。
    """

    # 读取应用配置
    settings = get_settings()

    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        max_retries=settings.openai_max_retries,
        timeout=settings.openai_timeout,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def get_chat_model(temperature: float = 0.0) -> ChatOpenAI:
    """
    获取对话与推理模型。

    相同温度参数会返回同一个模型实例。

    Args:
        temperature: 模型生成温度，默认为 0.0。

    Returns:
        已缓存的 ChatOpenAI 实例。

    Example:
        >>> model = get_chat_model()
        >>> creative_model = get_chat_model(0.7)
    """

    # 校验并规范化温度参数
    normalized_temperature = _normalize_temperature(temperature)
    return _get_chat_model_cached(normalized_temperature)


def clear_model_cache() -> None:
    """
    清除模型客户端和配置缓存。

    清除后，下一次调用模型工厂时将重新读取配置，
    并创建新的客户端实例。

    适用于：
    - 单元测试隔离
    - API Key 轮换
    - 模型配置更新
    - Base URL 更新
    """

    _get_chat_model_cached.cache_clear()
    get_embedding_model.cache_clear()
    clear_settings_cache()


def _normalize_temperature(temperature: float) -> float:
    """
    校验并规范化模型温度。

    将 0、0.0 等价参数统一转换成 float，
    避免产生语义相同但缓存键不同的模型实例。

    Args:
        temperature: 模型生成温度，范围为 0.0～2.0。

    Returns:
        规范化后的温度值。

    Raises:
        TypeError: 参数不是有效数值，或者传入 bool。
        ValueError: 参数不是有限数，或者不在合法范围内。
    """
    if isinstance(temperature, bool) or not isinstance(temperature, Real):
        raise TypeError("temperature must be a real number")

    normalized = float(temperature)

    if not math.isfinite(normalized):
        raise ValueError("temperature must be finite")

    if not 0.0 <= normalized <= 2.0:
        raise ValueError(
            "temperature must be between 0.0 and 2.0"
        )

    return normalized