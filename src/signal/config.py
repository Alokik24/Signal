from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Signal"
    app_version: str = "0.1.0"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_prefix="SIGNAL_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
