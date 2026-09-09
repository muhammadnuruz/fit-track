from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIM = 384


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    gender = sa.Enum("male", "female", name="gender")
    goal = sa.Enum("cut", "maintain", "bulk", name="goal")
    activity = sa.Enum(
        "sedentary", "light", "moderate", "active", "very_active", name="activity_level"
    )
    food_source = sa.Enum("open_db", "manual", "user", name="food_source")

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("gender", gender, nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("height_cm", sa.Numeric(5, 1), nullable=False),
        sa.Column("activity_level", activity, nullable=False),
        sa.Column("goal", goal, nullable=False),
        sa.Column("tdee", sa.Numeric(7, 1)),
        sa.Column("target_kcal", sa.Numeric(7, 1)),
        sa.Column("target_protein", sa.Numeric(6, 1)),
        sa.Column("target_carb", sa.Numeric(6, 1)),
        sa.Column("target_fat", sa.Numeric(6, 1)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "measurements",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 1), nullable=False),
        sa.Column("waist_cm", sa.Numeric(5, 1)),
        sa.Column("neck_cm", sa.Numeric(5, 1)),
        sa.Column("hip_cm", sa.Numeric(5, 1)),
        sa.Column("body_fat_pct", sa.Numeric(4, 1)),
        sa.Column("mood", sa.String(64)),
        sa.Column("photo_file_id", sa.String(256)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_measurements_user_id", "measurements", ["user_id"])

    op.create_table(
        "foods",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("name_normalized", sa.String(256), nullable=False),
        sa.Column("kcal", sa.Numeric(7, 2), nullable=False),
        sa.Column("protein", sa.Numeric(6, 2), nullable=False),
        sa.Column("carb", sa.Numeric(6, 2), nullable=False),
        sa.Column("fat", sa.Numeric(6, 2), nullable=False),
        sa.Column("source", food_source, nullable=False, server_default="manual"),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("embedding", Vector(EMBEDDING_DIM)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_foods_name_normalized", "foods", ["name_normalized"])

    op.create_table(
        "food_logs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("food_id", sa.BigInteger()),
        sa.Column("grams", sa.Numeric(7, 1), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("kcal", sa.Numeric(7, 2), nullable=False),
        sa.Column("protein", sa.Numeric(6, 2), nullable=False),
        sa.Column("carb", sa.Numeric(6, 2), nullable=False),
        sa.Column("fat", sa.Numeric(6, 2), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_food_logs_user_id", "food_logs", ["user_id"])
    op.create_index("ix_food_logs_logged_at", "food_logs", ["logged_at"])

    op.create_table(
        "daily_summary",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_kcal", sa.Numeric(8, 2), nullable=False, server_default="0"),
        sa.Column("total_protein", sa.Numeric(7, 2), nullable=False, server_default="0"),
        sa.Column("total_carb", sa.Numeric(7, 2), nullable=False, server_default="0"),
        sa.Column("total_fat", sa.Numeric(7, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_summary_user_date"),
    )
    op.create_index("ix_daily_summary_user_id", "daily_summary", ["user_id"])


def downgrade() -> None:
    op.drop_table("daily_summary")
    op.drop_table("food_logs")
    op.drop_table("foods")
    op.drop_table("measurements")
    op.drop_table("users")
    for enum_name in ("food_source", "activity_level", "goal", "gender"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
