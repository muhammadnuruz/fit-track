"""user_settings jadvali (til sozlamasi)

Revision ID: 0002_user_settings
Revises: 0001_initial
Create Date: 2026-09-08
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_user_settings"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    language = sa.Enum("uz", "ru", "en", name="language")
    op.create_table(
        "user_settings",
        sa.Column("telegram_id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("language", language, nullable=False, server_default="uz"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("user_settings")
    op.execute("DROP TYPE IF EXISTS language")
