"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00

This first migration materializes the full schema directly from the SQLAlchemy
model metadata, guaranteeing the initial database matches the ORM exactly.
Subsequent schema changes should be created with `alembic revision --autogenerate`.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

import app.models  # noqa: F401  (register models on metadata)
from app.database.base import Base

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
