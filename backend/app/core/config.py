from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Setting(BaseSettings):
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".envs/.env.local",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = ""
    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    SITE_NAME: str = ""

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 1025
    MAILPIT_UI_PORT: int = 8025

    REDIS_HOST: str = "redis"
    REDIS_PORT: str = 6379
    REDIS_DB: int = 0

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "password"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


settings = Setting()
