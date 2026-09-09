from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from app.i18n import DEFAULT_LANG, Lang, t
from app.services.settings import get_language


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
                lang = await get_language(session, tg_user.id)

        data["lang"] = lang
        effective = lang or DEFAULT_LANG

        def translate(key: str, **kwargs: object) -> str:
            return t(key, effective, **kwargs)

        data["_"] = translate
        return await handler(event, data)
