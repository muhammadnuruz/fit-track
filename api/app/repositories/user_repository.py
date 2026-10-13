from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def count(self) -> int:
        return (await self._session.execute(select(func.count()).select_from(User))).scalar_one()

    def add(self, user: User) -> None:
        self._session.add(user)

    async def delete_by_telegram_id(self, telegram_id: int) -> bool:
        stmt = delete(User).where(User.telegram_id == telegram_id).returning(User.id)
        return (await self._session.execute(stmt)).scalar_one_or_none() is not None
