"""Typed application settings, loaded from the environment or ``.env``."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "staging", "production"]


class Settings(BaseSettings):
    """All runtime configuration in one validated place."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    project_name: str = "FastAPI Hello"
    version: str = "0.1.0"
    environment: Environment = "local"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"
    docs_enabled: bool = True

    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = True

    default_locale: str = "en"
    cors_origins: tuple[str, ...] = ()

    @property
    def is_production(self) -> bool:
        """True when running with production safeguards enabled."""
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()
