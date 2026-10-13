from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_settings import UserSettings


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def user_exists(session: AsyncSession, telegram_id: int) -> bool:
    stmt = select(User.id).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def delete_user_completely(session: AsyncSession, telegram_id: int) -> bool:
    user = await get_by_telegram_id(session, telegram_id)
    settings_id = (
        await session.execute(
            select(UserSettings.telegram_id).where(UserSettings.telegram_id == telegram_id)
        )
    ).scalar_one_or_none()
    if user is None and settings_id is None:
        return False
    if user is not None:
        await session.execute(delete(User).where(User.telegram_id == telegram_id))
    if settings_id is not None:
        await session.execute(delete(UserSettings).where(UserSettings.telegram_id == telegram_id))
    await session.commit()
    return True
