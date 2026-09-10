from __future__ import annotations

import contextlib
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from app.cache import get_redis


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
        if user is not None and not await self._allow(user.id):
            return None
        return await handler(event, data)

    async def _allow(self, user_id: int) -> bool:
        # Redis bo'lsa — replica'lar orasida umumiy throttle (atomik SET NX PX).
        redis = get_redis()
        if redis is not None:
            with contextlib.suppress(Exception):  # redis xato → in-memory
                ok = await redis.set(
                    f"thr:{user_id}", "1", nx=True, px=max(1, int(self.rate * 1000))
                )
                return bool(ok)
        now = time.monotonic()
        last = self._last.get(user_id, 0.0)
        if now - last < self.rate:
            return False
        self._last[user_id] = now
        if len(self._last) % 1000 == 0:
            self._evict(now)
        return True
