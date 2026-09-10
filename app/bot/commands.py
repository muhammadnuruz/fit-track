from __future__ import annotations

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    MenuButtonCommands,
    MenuButtonWebApp,
    WebAppInfo,
)

from app.config import settings
from app.i18n import DEFAULT_LANG, LANGUAGES, Lang, t


def _commands_for(lang: Lang) -> list[BotCommand]:
    return [
        BotCommand(command="start", description=t("cmd_start_desc", lang)),
        BotCommand(command="help", description=t("cmd_help_desc", lang)),
    ]


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(_commands_for(DEFAULT_LANG), scope=BotCommandScopeDefault())
    for info in LANGUAGES:
        await bot.set_my_commands(
            _commands_for(info.code),
            scope=BotCommandScopeDefault(),
            language_code=info.code.value,
        )


async def setup_menu_button(bot: Bot) -> None:
    """Xabar qatori yonidagi doimiy tugmani Mini App'ni ochadigan qiladi.
    webapp_url https bo'lmasa — oddiy 'komandalar' tugmasi qoladi."""
    base = settings.webapp_url.strip()
    if base.startswith("https://"):
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="FitTrack", web_app=WebAppInfo(url=base))
        )
    else:
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
