from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IntPKMixin, TimestampMixin


class Measurement(IntPKMixin, TimestampMixin, Base):
    __tablename__ = "measurements"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    waist_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    neck_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    hip_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    body_fat_pct: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    mood: Mapped[str | None] = mapped_column(String(64))
    photo_file_id: Mapped[str | None] = mapped_column(String(256))
