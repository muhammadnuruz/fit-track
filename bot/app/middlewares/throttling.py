import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class ThrottlingMiddleware(BaseMiddleware):
    _TTL = 300.0
    _MAX_ENTRIES = 50_000

    def __init__(self, rate: float = 0.5) -> None:
        self.rate = rate
        self._last: dict[int, float] = {}

    def _evict(self, now: float) -> None:
        cutoff = now - self._TTL
        for user_id in [uid for uid, ts in self._last.items() if ts < cutoff]:
            del self._last[user_id]
        if len(self._last) > self._MAX_ENTRIES:
            oldest = sorted(self._last.items(), key=lambda item: item[1])
            for user_id, _ in oldest[: len(self._last) - self._MAX_ENTRIES]:
                del self._last[user_id]

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is not None and not self._allow(user.id):
            return None
        return await handler(event, data)

    def _allow(self, user_id: int) -> bool:
        now = time.monotonic()
        last = self._last.get(user_id, 0.0)
        if now - last < self.rate:
            return False
        self._last[user_id] = now
        if len(self._last) % 1000 == 0:
            self._evict(now)
        return True
