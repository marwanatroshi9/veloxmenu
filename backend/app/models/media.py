from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, IntPKMixin, TimestampMixin


class Media(Base, IntPKMixin, TimestampMixin):
    """Record of an uploaded asset (Cloudinary). Used for storage accounting."""

    __tablename__ = "media"

    restaurant_id: Mapped[int | None] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), index=True
    )
    public_id: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), default="image", nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    purpose: Mapped[str | None] = mapped_column(String(64))  # logo | cover | category | item
