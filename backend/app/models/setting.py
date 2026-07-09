from __future__ import annotations

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, IntPKMixin, TimestampMixin


class Setting(Base, IntPKMixin, TimestampMixin):
    """Key/value settings, optionally scoped per restaurant (NULL = global)."""

    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("restaurant_id", "key", name="uq_setting_scope_key"),)

    restaurant_id: Mapped[int | None] = mapped_column(index=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str | None] = mapped_column(Text)
