"""SQLAlchemy 2.0 asosiy sinflari — barcha modellar shundan meros oladi."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Barcha ORM modellari uchun umumiy asos."""


class TimestampMixin:
    """`created_at` ustunini beruvchi mixin."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class IntPKMixin:
    """Butun son (BIGINT) birlamchi kalit."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
