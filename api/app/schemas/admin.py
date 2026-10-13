from pydantic import BaseModel


class StatsOut(BaseModel):
    total_users: int
    profiles: int
    by_language: dict[str, int]


class TelegramIdsOut(BaseModel):
    telegram_ids: list[int]
