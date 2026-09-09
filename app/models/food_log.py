
from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IntPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.food import Food
    from app.models.user import User


class FoodLog(Base, IntPKMixin):

    __tablename__ = "food_logs"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    food_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("foods.id", ondelete="SET NULL")
    )
    grams: Mapped[float] = mapped_column(Numeric(7, 1), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )

    kcal: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    carb: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    fat: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)

    user: Mapped[User] = relationship(back_populates="food_logs")
    food: Mapped[Food | None] = relationship()

    def __repr__(self) -> str:
        return f"<FoodLog user={self.user_id} food={self.food_id} g={self.grams}>"


class DailySummary(Base, IntPKMixin, TimestampMixin):

    __tablename__ = "daily_summary"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_daily_summary_user_date"),)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[date_type] = mapped_column(Date, nullable=False)

    total_kcal: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    total_protein: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    total_carb: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    total_fat: Mapped[float] = mapped_column(Numeric(7, 2), default=0, nullable=False)
