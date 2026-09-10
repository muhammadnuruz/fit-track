from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0003_drop_food_embedding"
down_revision: str | None = "0002_user_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("foods", "embedding")


def downgrade() -> None:
    op.add_column("foods", sa.Column("embedding", Vector(384), nullable=True))
