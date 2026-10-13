import re
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

WEBHOOK_SECRET_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,256}$")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = ""
    bot_mode: Literal["polling", "webhook"] = "polling"
    webhook_base_url: str = ""
    webhook_path: str = "/webhook"
    webhook_secret: str = ""
    web_host: str = "0.0.0.0"
    web_port: int = 8080

    api_base_url: str = "http://localhost:8000"
    api_key: str = ""
    admins: str = ""
    redis_url: str = ""
    log_level: str = "INFO"

    @property
    def admin_ids(self) -> list[int]:
        return [int(part) for part in self.admins.split(",") if part.strip().isdigit()]


def validate_settings(config: Settings) -> list[str]:
    errors: list[str] = []
    if not config.bot_token:
        errors.append("BOT_TOKEN is required")
    if not config.api_key:
        errors.append("API_KEY is required")
    if config.bot_mode == "webhook":
        if not config.webhook_base_url.startswith("https://"):
            errors.append("WEBHOOK_BASE_URL must be a public https:// URL in webhook mode")
        if not WEBHOOK_SECRET_PATTERN.fullmatch(config.webhook_secret):
            errors.append("WEBHOOK_SECRET must be 16-256 characters: letters, digits, _ or -")
        if not config.webhook_path.startswith("/"):
            errors.append("WEBHOOK_PATH must start with /")
    return errors


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
