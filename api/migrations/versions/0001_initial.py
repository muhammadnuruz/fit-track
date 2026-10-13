from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("gender", sa.Enum("male", "female", name="gender"), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("height_cm", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column(
            "activity_level",
            sa.Enum(
                "sedentary",
                "light",
                "moderate",
                "active",
                "very_active",
                name="activity_level",
            ),
            nullable=False,
        ),
        sa.Column("goal", sa.Enum("cut", "maintain", "bulk", name="goal"), nullable=False),
        sa.Column("tdee", sa.Numeric(precision=7, scale=1), nullable=True),
        sa.Column("target_kcal", sa.Numeric(precision=7, scale=1), nullable=True),
        sa.Column("target_protein", sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column("target_carb", sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column("target_fat", sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    op.create_table(
        "measurements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column("waist_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("neck_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("hip_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("body_fat_pct", sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column("mood", sa.String(length=64), nullable=True),
        sa.Column("photo_file_id", sa.String(length=256), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_measurements_user_id"), "measurements", ["user_id"], unique=False)

    op.create_table(
        "user_settings",
        sa.Column("telegram_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column(
            "language",
            sa.Enum("uz", "ru", "en", name="language"),
            server_default="uz",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("telegram_id"),
    )


def downgrade() -> None:
    op.drop_table("user_settings")
    op.drop_index(op.f("ix_measurements_user_id"), table_name="measurements")
    op.drop_table("measurements")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
    for name in ("language", "goal", "activity_level", "gender"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
