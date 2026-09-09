
from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.db.base import Base, IntPKMixin, TimestampMixin, pg_enum
from app.models.enums import FoodSource


class Food(Base, IntPKMixin, TimestampMixin):

    __tablename__ = "foods"

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(256), index=True, nullable=False)

    kcal: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    carb: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    fat: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)

    source: Mapped[FoodSource] = mapped_column(
        pg_enum(FoodSource, "food_source"), default=FoodSource.MANUAL, nullable=False
    )
    is_approved: Mapped[bool] = mapped_column(default=True, nullable=False)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.embedding_dim))

    def __repr__(self) -> str:
        return f"<Food id={self.id} name={self.name!r} kcal={self.kcal}>"
