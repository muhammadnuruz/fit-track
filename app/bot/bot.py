from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

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


def _make_storage() -> BaseStorage:
    # Redis bo'lsa — FSM holati replica'lar orasida bo'linadi va restart' да saqlanadi.
    if settings.redis_url:
        return RedisStorage.from_url(settings.redis_url)
    return MemoryStorage()


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=_make_storage())

    for observer in (dp.message, dp.callback_query):
        observer.middleware(ThrottlingMiddleware())
        observer.middleware(PrivateOnlyMiddleware())
        observer.middleware(DbSessionMiddleware())
        observer.middleware(LanguageMiddleware())

    dp.include_router(admin.router)
    dp.include_router(common.router)
    return dp
