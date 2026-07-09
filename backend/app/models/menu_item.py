from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, IntPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.restaurant import Restaurant


class SpicyLevel(int, enum.Enum):
    NONE = 0
    MILD = 1
    MEDIUM = 2
    HOT = 3
    EXTRA_HOT = 4


class MenuItem(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "menu_items"

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(512))

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_price: Mapped[float | None] = mapped_column(Numeric(10, 2))

    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    preparation_time: Mapped[int | None] = mapped_column(Integer)  # minutes
    calories: Mapped[int | None] = mapped_column(Integer)
    spicy_level: Mapped[SpicyLevel] = mapped_column(
        Enum(SpicyLevel, native_enum=False), default=SpicyLevel.NONE, nullable=False
    )

    # Stored as JSON-encoded string arrays (validated at the schema layer).
    ingredients: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(Text)

    # Per-language overrides for name/description, JSON:
    # {"ar": {"name": "...", "description": "..."}, "ckb": {...}}
    # The base name/description are the primary (default) language.
    translations: Mapped[str | None] = mapped_column(Text)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    restaurant: Mapped["Restaurant"] = relationship(back_populates="menu_items")
    category: Mapped["Category"] = relationship(back_populates="menu_items")
