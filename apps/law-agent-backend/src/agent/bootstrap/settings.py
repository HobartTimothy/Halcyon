from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_prefix="EA_",
        env_file=".env",
        extra="forbid",
        frozen=True,
    )

    environment: Environment = Environment.DEVELOPMENT
    service_name: str = "enterprise-agent-api"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    model_gateway_url: str = "http://litellm:4000"
    broker_url: str = "amqp://guest:guest@rabbitmq:5672//"
    result_backend_url: str = "redis://valkey:6379/1"
    realtime_stream_url: str = "redis://valkey:6379/0"
    database_url: str = Field(
        default="postgresql+psycopg://enterprise:enterprise@postgres:5432/enterprise"
    )

    openai_api_key: SecretStr | None = None
    openai_base_url: str | None = None
    openai_chat_model: str = "deepseek-v4-pro"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_timeout: float = Field(default=30.0, gt=0)
    openai_max_retries: int = Field(default=2, ge=0, le=10)

    @field_validator("openai_base_url", mode="before")
    @classmethod
    def normalize_openai_base_url(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:

    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
