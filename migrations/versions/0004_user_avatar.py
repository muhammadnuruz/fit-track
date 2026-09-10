from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_user_avatar"
down_revision: str | None = "0003_drop_food_embedding"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_path", sa.String(length=256), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_path")
