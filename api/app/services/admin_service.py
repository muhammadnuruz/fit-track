from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.schemas.admin import StatsOut


async def get_stats(session: AsyncSession) -> StatsOut:
    by_language = await UserSettingsRepository(session).count_by_language()
    return StatsOut(
        total_users=sum(by_language.values()),
        profiles=await UserRepository(session).count(),
        by_language={language.value: count for language, count in by_language.items()},
    )


async def list_telegram_ids(session: AsyncSession) -> list[int]:
    return await UserSettingsRepository(session).list_telegram_ids()


async def delete_user(session: AsyncSession, telegram_id: int) -> bool:
    users_deleted = await UserRepository(session).delete_by_telegram_id(telegram_id)
    settings_deleted = await UserSettingsRepository(session).delete(telegram_id)
    await session.commit()
    return users_deleted or settings_deleted
