"""add translations columns to categories and menu_items

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-03 00:00:00

Idempotent for the same reason as 0002 (see its docstring).
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    if not _has_column("categories", "translations"):
        op.add_column("categories", sa.Column("translations", sa.Text(), nullable=True))
    if not _has_column("menu_items", "translations"):
        op.add_column("menu_items", sa.Column("translations", sa.Text(), nullable=True))


def downgrade() -> None:
    if _has_column("menu_items", "translations"):
        op.drop_column("menu_items", "translations")
    if _has_column("categories", "translations"):
        op.drop_column("categories", "translations")
