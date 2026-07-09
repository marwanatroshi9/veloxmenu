from __future__ import annotations

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant


def unique_restaurant_slug(db: Session, name: str, base: str | None = None) -> str:
    """Generate a URL-safe slug unique across restaurants."""
    root = slugify(base or name)[:200] or "restaurant"
    candidate = root
    suffix = 2
    while db.scalar(select(Restaurant.id).where(Restaurant.slug == candidate)) is not None:
        candidate = f"{root}-{suffix}"
        suffix += 1
    return candidate
