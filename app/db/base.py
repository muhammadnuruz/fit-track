"""SQLAlchemy 2.0 asosiy sinflari — barcha modellar shundan meros oladi."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TypeVar

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_E = TypeVar("_E", bound=enum.Enum)


def pg_enum(enum_cls: type[_E], name: str) -> SAEnum:
    """PostgreSQL enum ustuni — nom emas, ENUM QIYMATLARINI ('uz','male'...) saqlaydi.

    SQLAlchemy sukut bo'yicha enum a'zosining `.name` ini (masalan "RU") saqlaydi;
    bizning PG tiplarimiz esa `.value` ('ru') ustiga qurilgan. `values_callable`
    shu nomuvofiqlikni bartaraf qiladi.
    """
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda e: [member.value for member in e],
    )


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
