from __future__ import annotations

from decimal import Decimal

from sqlalchemy import BigInteger, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IntPKMixin, TimestampMixin, pg_enum
from app.models.enums import ActivityLevel, Gender, Goal


class User(IntPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    # yuklangan avatar URL yo'li; bo'sh bo'lsa Telegram rasmi yoki monogramma
    avatar_path: Mapped[str | None] = mapped_column(String(256))
    gender: Mapped[Gender] = mapped_column(pg_enum(Gender, "gender"), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    activity_level: Mapped[ActivityLevel] = mapped_column(
        pg_enum(ActivityLevel, "activity_level"), nullable=False
    )
    goal: Mapped[Goal] = mapped_column(pg_enum(Goal, "goal"), nullable=False)
    tdee: Mapped[Decimal | None] = mapped_column(Numeric(7, 1))
    target_kcal: Mapped[Decimal | None] = mapped_column(Numeric(7, 1))
    target_protein: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    target_carb: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    target_fat: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
