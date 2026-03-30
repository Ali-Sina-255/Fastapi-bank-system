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

    # =========================================
    # 🌐 Project
    # =========================================
    API_V1_STR: str = ""
    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    SITE_NAME: str = ""

    # =========================================
    # 🐘 Database
    # =========================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # =========================================
    # 📧 Email (SMTP)
    # =========================================
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = ""
    SUPPORT_EMAIL: str = ""

    SMTP_HOST: str
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    EMAIL_USE_TLS: bool = False
    EMAIL_USE_SSL: bool = False

    # =========================================
    # 🔴 Redis
    # =========================================
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # =========================================
    # 🐇 RabbitMQ
    # =========================================
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    # =========================================
    #  JWT Cookies
    # =========================================
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTES: int = 30 if ENVIRONMENT == "local" else 15
    JWT_REFRESH_TOKEN_EXPIRATION_DAYS: int = 1
    COOKIE_SECURE: bool = False if ENVIRONMENT == "local" else True
    COOKIE_ACCESS_NAME: str = "access_token"
    COOKIE_REFRESH_NAME: str = "refresh_token"
    COOKIE_LOGGED_IN_NAME: str = "logged_in"

    COOKIE_HTTP_ONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/"
    SIGNING_KEY: str = ""

    @property
    def CELERY_BROKER_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
        )

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    # =========================================
    # 🔐 Security
    # =========================================
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOGIN_ATTEMPTS: int = 3

    # =========================================
    # 🌍 API
    # =========================================
    API_BASE_URL: str = ""

    # =========================================
    # ⏱️ Dynamic Settings
    # =========================================
    @property
    def OTP_EXPIRATION_MINUTES(self) -> int:
        return 2 if self.ENVIRONMENT == "local" else 5

    @property
    def LOCKOUT_DURATION_MINUTES(self) -> int:
        return 5

    @property
    def ACTIVATION_TOKEN_EXPIRATION_MINUTES(self) -> int:
        return 5

    # =========================================
    # 🐘 DATABASE URL
    # =========================================
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


settings = Setting()
