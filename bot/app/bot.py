from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from app.api_client import ApiClient
from app.config import settings
from app.handlers import admin, common, onboarding, profile
from app.middlewares.i18n import LanguageMiddleware
from app.middlewares.private_only import PrivateOnlyMiddleware
from app.middlewares.throttling import ThrottlingMiddleware


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def _make_storage() -> BaseStorage:
    if settings.redis_url:
        return RedisStorage.from_url(settings.redis_url)
    return MemoryStorage()


def create_dispatcher(api: ApiClient) -> Dispatcher:
    dp = Dispatcher(storage=_make_storage(), api=api)

    for observer in (dp.message, dp.callback_query):
        observer.middleware(ThrottlingMiddleware())
        observer.middleware(PrivateOnlyMiddleware())
        observer.middleware(LanguageMiddleware())

    dp.include_router(admin.router)
    dp.include_router(onboarding.router)
    dp.include_router(profile.router)
    dp.include_router(common.router)
    return dp
