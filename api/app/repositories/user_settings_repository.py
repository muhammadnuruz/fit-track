from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Language
from app.models.user_settings import UserSettings


class UserSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, telegram_id: int) -> UserSettings | None:
        return await self._session.get(UserSettings, telegram_id)

    def add(self, row: UserSettings) -> None:
        self._session.add(row)

    async def list_telegram_ids(self) -> list[int]:
        stmt = select(UserSettings.telegram_id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def count_by_language(self) -> dict[Language, int]:
        stmt = select(UserSettings.language, func.count()).group_by(UserSettings.language)
        rows = (await self._session.execute(stmt)).all()
        counts = dict.fromkeys(Language, 0)
        for language, count in rows:
            counts[language] = count
        return counts

    async def delete(self, telegram_id: int) -> bool:
        stmt = (
            delete(UserSettings)
            .where(UserSettings.telegram_id == telegram_id)
            .returning(UserSettings.telegram_id)
        )
        return (await self._session.execute(stmt)).scalar_one_or_none() is not None
