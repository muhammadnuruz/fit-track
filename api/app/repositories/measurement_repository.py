from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.measurement import Measurement


class MeasurementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def latest_for_user(self, user_id: int) -> Measurement | None:
        stmt = (
            select(Measurement)
            .where(Measurement.user_id == user_id)
            .order_by(Measurement.date.desc(), Measurement.id.desc())
            .limit(1)
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def for_day(self, user_id: int, day: date) -> Measurement | None:
        stmt = select(Measurement).where(Measurement.user_id == user_id, Measurement.date == day)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    def add(self, measurement: Measurement) -> None:
        self._session.add(measurement)
