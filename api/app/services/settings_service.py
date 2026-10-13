from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Language
from app.models.user_settings import UserSettings
from app.repositories.user_settings_repository import UserSettingsRepository


async def get_language(session: AsyncSession, telegram_id: int) -> Language | None:
    row = await UserSettingsRepository(session).get(telegram_id)
    return row.language if row is not None else None


async def set_language(session: AsyncSession, telegram_id: int, language: Language) -> Language:
    repository = UserSettingsRepository(session)
    row = await repository.get(telegram_id)
    if row is None:
        row = UserSettings(telegram_id=telegram_id, language=language)
        repository.add(row)
    else:
        row.language = language
    await session.commit()
    return row.language
