from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROMPTLAB_", extra="ignore")

    env: str = "dev"
    jwt_secret: str = "change-me"
    jwt_issuer: str = "promptlab"
    jwt_audience: str = "promptlab"
    jwt_exp_minutes: int = 60
    cors_origins: str = "*"
    rate_limit: str = "60/minute"

    database_url: str = "postgresql+psycopg://promptlab:promptlab@postgres:5432/promptlab"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
