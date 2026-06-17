"""Typed application configuration, loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "ie"
    job_location: str = "Dublin"


settings = Settings()
