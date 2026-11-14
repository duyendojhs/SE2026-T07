"""Add local Issue title undo snapshot fields."""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "a8d7c6e5f401"
down_revision: str | Sequence[str] | None = "3ffc12e866fb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "issues",
        sa.Column("previous_title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    )
    op.add_column("issues", sa.Column("title_change_sync_id", sa.Uuid(), nullable=True))


def downgrade() -> None:
    op.drop_column("issues", "title_change_sync_id")
    op.drop_column("issues", "previous_title")
