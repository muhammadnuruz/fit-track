from __future__ import annotations

import contextlib
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.i18n import DEFAULT_LANG, Lang, t
from app.services.settings import get_language

_LANG_TTL = 3600  # sekund


async def _cached_language(session: AsyncSession, telegram_id: int) -> Lang | None:
    redis = get_redis()
    if redis is not None:
        try:
            cached = await redis.get(f"lang:{telegram_id}")
            if cached == "-":
                return None  # "til o'rnatilmagan" ni ham cache qilamiz
            if cached:
                return Lang(cached)
        except Exception:  # redis xato → DB'ga o'tamiz
            redis = None
    lang = await get_language(session, telegram_id)
    if redis is not None:
        with contextlib.suppress(Exception):
            await redis.set(f"lang:{telegram_id}", lang.value if lang else "-", ex=_LANG_TTL)
    return lang


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        lang: Lang | None = None

        if tg_user is not None:
            session = data.get("session")
            if session is not None:
                lang = await _cached_language(session, tg_user.id)

        data["lang"] = lang
        effective = lang or DEFAULT_LANG

        def translate(key: str, **kwargs: object) -> str:
            return t(key, effective, **kwargs)

        data["_"] = translate
        return await handler(event, data)
