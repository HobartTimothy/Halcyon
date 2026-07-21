"""Strict application settings loaded from environment variables."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Immutable runtime settings.

    Unknown fields are rejected so configuration mistakes fail during startup.
    """

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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""

    return Settings()
