from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    frontend_origins: Annotated[list[AnyHttpUrl], NoDecode]
    supabase_url: str
    supabase_publishable_key: str
    supabase_secret_key: str | None = None
    database_url: str | None = None

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def split_frontend_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return value

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    # BaseSettings loads required fields from environment variables.
    return Settings()  # type: ignore[call-arg]
