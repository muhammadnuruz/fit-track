import contextlib
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from app.api_client import ApiClient, ApiError
from app.i18n import DEFAULT_LANG, Lang, t


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
            api: ApiClient = data["api"]
            try:
                lang = await api.get_language(tg_user.id)
            except ApiError:
                await _reply_unavailable(event)
                return None

        data["lang"] = lang
        return await handler(event, data)


async def _reply_unavailable(event: TelegramObject) -> None:
    text = t("service_unavailable", DEFAULT_LANG)
    with contextlib.suppress(Exception):
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
