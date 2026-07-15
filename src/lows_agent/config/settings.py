from pathlib import Path
from functools import lru_cache
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 假设文件路径：
# 项目根目录/src/lows_agent/config/settings.py
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """应用配置。"""

    # 必填；未配置时在应用启动阶段直接报错
    openai_api_key: SecretStr

    openai_base_url: str | None = None

    # 默认等于聊天模型，但可以配置不同的模型
    openai_chat_model: str = "deepseek-v4-pro"

    # 不要默认等于聊天模型，要求显式配置
    openai_embedding_model: str

    # 默认 30 秒，最小值 1 秒
    openai_timeout: float = Field(default=30.0, gt=0)

    # 默认 2 次，最小值 0 次，最大值 10 次
    openai_max_retries: int = Field(default=2, ge=0, le=10)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("openai_base_url", mode="before")
    @classmethod
    def normalize_base_url(cls, value: object) -> object:
        """将空字符串转换为 None，并清理首尾空格。"""

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取缓存后的应用配置。"""
    return Settings()


def clear_settings_cache() -> None:
    """清除配置缓存，使下一次调用重新加载配置。"""

    get_settings.cache_clear()
