"""Aiogram bot va dispatcher fabrikasi."""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import common
from app.config import settings


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    # MVP: MemoryStorage. Production'da Redis storage ga o'tiladi.
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common.router)
    # Kelajakda: onboarding, logging, checkin routerlari shu yerga qo'shiladi.
    return dp
