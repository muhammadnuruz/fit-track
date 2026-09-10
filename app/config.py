from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    bot_token: str = Field(default="", description="@BotFather tokeni")
    bot_mode: Literal["polling", "webhook"] = "polling"
    webhook_url: str = ""
    webhook_path: str = "/webhook"
    webhook_secret: str = ""
    webapp_url: str = ""
    bot_username: str = ""  # landing sahifasidagi "Telegramda ochish" tugmasi uchun (@ siz)

    postgres_user: str = "fittrack"
    postgres_password: str = "fittrack"
    postgres_db: str = "fittrack"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str = ""

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384

    log_level: str = "INFO"
    tz: str = "Asia/Tashkent"
    env: Literal["development", "production", "test"] = "development"
    admins: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_dsn(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_dsn_sync(self) -> str:
        return self.db_dsn.replace("+asyncpg", "+psycopg2")

    @property
    def admin_ids(self) -> list[int]:
        ids: list[int] = []
        for part in self.admins.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        return ids


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
