import enum
from datetime import datetime
from typing import TypeVar

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

E = TypeVar("E", bound=enum.Enum)


def pg_enum(enum_cls: type[E], name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda members: [member.value for member in members],
    )


class Base(DeclarativeBase):
    pass


class IntPKMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
