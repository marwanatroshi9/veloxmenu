"""add category.icon column

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-02 00:00:00

Idempotent: the baseline migration (0001) materializes the schema from the ORM
metadata, so on a fresh database the `icon` column may already exist. We only add
it when missing, which also lets databases created before this column upgrade
cleanly.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    if not _has_column("categories", "icon"):
        op.add_column("categories", sa.Column("icon", sa.String(length=40), nullable=True))


def downgrade() -> None:
    if _has_column("categories", "icon"):
        op.drop_column("categories", "icon")
