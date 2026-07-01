"""Typed application configuration, loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jooble_api_key: str = ""
    careerjet_affiliate_id: str = ""
    job_location: str = "Dublin, Ireland"


settings = Settings()
