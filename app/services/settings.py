"""Foydalanuvchi sozlamalari xizmati — til o'qish/yozish (upsert)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n.languages import Lang
from app.models.user_settings import UserSettings


async def get_language(session: AsyncSession, telegram_id: int) -> Lang | None:
    """Tanlangan tilni qaytaradi; hali tanlanmagan bo'lsa None."""
    row = await session.get(UserSettings, telegram_id)
    return row.language if row else None


async def set_language(session: AsyncSession, telegram_id: int, language: Lang) -> UserSettings:
    """Tilni saqlaydi (mavjud bo'lsa yangilaydi, bo'lmasa yaratadi)."""
    row = await session.get(UserSettings, telegram_id)
    if row is None:
        row = UserSettings(telegram_id=telegram_id, language=language)
        session.add(row)
    else:
        row.language = language
    await session.flush()
    return row


async def has_language(session: AsyncSession, telegram_id: int) -> bool:
    stmt = select(UserSettings.telegram_id).where(UserSettings.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none() is not None
