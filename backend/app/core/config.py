from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

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

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # Email
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "password"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOGIN_ATTEMPTS: int = 3
    
    API_BASE_URL:str = ''
    SUPPORT_EMAIL:str = ''
    JWT_SECRET_KEY:str = ''
    JWT_ALGORITHM :str = 'HS256'
    
    @property
    def OTP_EXPIRATION_MINUTES(self) -> int:
        return 2 if self.ENVIRONMENT == "local" else 5

    @property
    def LOCKOUT_DURATION_MINUTES(self) -> int:
        return 5 if self.ENVIRONMENT == "local" else 5

    @property
    def ACTIVATION_TOKEN_EXPIRATION_MINUTES(self) -> int:
        return 5 if self.ENVIRONMENT == "local" else 5

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


settings = Setting()  # type: ignore
