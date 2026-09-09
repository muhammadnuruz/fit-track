from __future__ import annotations

import contextlib
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Chat, Message, TelegramObject

from app.bot.emoji import PRIVATE_CHAT_EMOJI_ID, custom_emoji

GROUP_NOTICE = (
    f'{custom_emoji(PRIVATE_CHAT_EMOJI_ID, "🔒")} '
    "Kechirasiz men faqat shaxsiy chatda ishlay olaman."
)


class PrivateOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat | None = data.get("event_chat")
        if chat is not None and chat.id < 0:
            if isinstance(event, Message):
                with contextlib.suppress(Exception):
                    await event.answer(GROUP_NOTICE)
            elif isinstance(event, CallbackQuery):
                with contextlib.suppress(Exception):
                    await event.answer(GROUP_NOTICE, show_alert=True)
            return None
        return await handler(event, data)
