from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot import admin
from app.bot.handlers import common
from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.middlewares.i18n import LanguageMiddleware
from app.bot.middlewares.private_only import PrivateOnlyMiddleware
from app.bot.middlewares.throttling import ThrottlingMiddleware
from app.config import settings


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    for observer in (dp.message, dp.callback_query):
        observer.middleware(ThrottlingMiddleware())
        observer.middleware(PrivateOnlyMiddleware())
        observer.middleware(DbSessionMiddleware())
        observer.middleware(LanguageMiddleware())

    dp.include_router(admin.router)
    dp.include_router(common.router)
    return dp
