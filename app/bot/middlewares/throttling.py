from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class ThrottlingMiddleware(BaseMiddleware):
    # Xotira sizishining oldini olish: eski yozuvlar davriy tozalanadi va
    # umumiy hajm cheklanadi. (Ko'p-replica uchun buni Redis TTL ga ko'chirish kerak.)
    _TTL = 300.0  # yozuv 5 daqiqadan keyin eskiradi
    _MAX_ENTRIES = 50_000

    def __init__(self, rate: float = 0.5) -> None:
        self.rate = rate
        self._last: dict[int, float] = {}

    def _evict(self, now: float) -> None:
        cutoff = now - self._TTL
        stale = [uid for uid, ts in self._last.items() if ts < cutoff]
        for uid in stale:
            del self._last[uid]
        # Xavfsizlik chegarasi: baribir juda katta bo'lib ketsa, eng eskilarni olib tashlaymiz.
        if len(self._last) > self._MAX_ENTRIES:
            for uid, _ in sorted(self._last.items(), key=lambda kv: kv[1])[
                : len(self._last) - self._MAX_ENTRIES
            ]:
                del self._last[uid]

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is not None:
            now = time.monotonic()
            last = self._last.get(user.id, 0.0)
            if now - last < self.rate:
                return None
            self._last[user.id] = now
            if len(self._last) % 1000 == 0:
                self._evict(now)
        return await handler(event, data)
