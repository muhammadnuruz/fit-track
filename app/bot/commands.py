"""Telegram buyruqlar menyusi — har bir til uchun alohida o'rnatiladi."""

from __future__ import annotations

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.i18n import DEFAULT_LANG, LANGUAGES, Lang, t


def _commands_for(lang: Lang) -> list[BotCommand]:
    # Til almashtirish endi buyruq emas, doimiy reply-knopka orqali.
    return [
        BotCommand(command="start", description=t("cmd_start_desc", lang)),
        BotCommand(command="help", description=t("cmd_help_desc", lang)),
    ]


async def setup_bot_commands(bot: Bot) -> None:
    """Standart (default) va har til uchun buyruqlar ro'yxatini o'rnatadi.

    Telegram foydalanuvchining ilova tiliga qarab mos ro'yxatni ko'rsatadi;
    zaxira sifatida DEFAULT_LANG standart scope'ga qo'yiladi.
    """
    await bot.set_my_commands(_commands_for(DEFAULT_LANG), scope=BotCommandScopeDefault())
    for info in LANGUAGES:
        await bot.set_my_commands(
            _commands_for(info.code),
            scope=BotCommandScopeDefault(),
            language_code=info.code.value,
        )
