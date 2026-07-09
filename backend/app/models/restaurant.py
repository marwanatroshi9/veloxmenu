from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, IntPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.menu_item import MenuItem
    from app.models.subscription import Subscription
    from app.models.user import User


class RestaurantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class Restaurant(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "restaurants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    status: Mapped[RestaurantStatus] = mapped_column(
        Enum(RestaurantStatus, native_enum=False, length=32),
        default=RestaurantStatus.ACTIVE,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(Text)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(512))
    cover_url: Mapped[str | None] = mapped_column(String(512))
    theme_color: Mapped[str] = mapped_column(String(9), default="#E11D48", nullable=False)

    # Contact / social
    phone: Mapped[str | None] = mapped_column(String(40))
    whatsapp: Mapped[str | None] = mapped_column(String(40))
    instagram: Mapped[str | None] = mapped_column(String(255))
    facebook: Mapped[str | None] = mapped_column(String(255))
    tiktok: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))

    # Location / hours (opening_hours stored as JSON string per day)
    address: Mapped[str | None] = mapped_column(String(512))
    google_maps_url: Mapped[str | None] = mapped_column(String(512))
    opening_hours: Mapped[str | None] = mapped_column(Text)  # JSON string

    # Localization
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    default_language: Mapped[str] = mapped_column(String(8), default="en", nullable=False)

    managers: Mapped[list["User"]] = relationship(
        back_populates="restaurant",
        foreign_keys="User.restaurant_id",
        cascade="all, delete-orphan",
    )
    categories: Mapped[list["Category"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    menu_items: Mapped[list["MenuItem"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan", uselist=False
    )

    @property
    def is_active(self) -> bool:
        return self.status == RestaurantStatus.ACTIVE
