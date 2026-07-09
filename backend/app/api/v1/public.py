from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.session import get_db
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant, RestaurantStatus
from app.schemas.public import (
    PublicCategory,
    PublicMenuItem,
    PublicMenuResponse,
    PublicRestaurant,
)

router = APIRouter(prefix="/public", tags=["public"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/restaurants/{slug}", response_model=PublicMenuResponse)
def get_public_menu(slug: str, db: DbSession):
    """Return the full public menu for an active restaurant by slug.

    Only visible categories, available items, and active restaurants are exposed.
    """
    restaurant = db.scalar(
        select(Restaurant).where(
            Restaurant.slug == slug, Restaurant.status == RestaurantStatus.ACTIVE
        )
    )
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    categories = db.scalars(
        select(Category)
        .where(Category.restaurant_id == restaurant.id, Category.is_visible.is_(True))
        .order_by(Category.sort_order.asc(), Category.id.asc())
        .options(selectinload(Category.menu_items))
    ).all()

    public_categories: list[PublicCategory] = []
    featured: list[PublicMenuItem] = []
    for category in categories:
        items = sorted(
            (i for i in category.menu_items if i.is_available),
            key=lambda i: (i.sort_order, i.id),
        )
        public_items = [PublicMenuItem.model_validate(i) for i in items]
        featured.extend(pi for pi, i in zip(public_items, items) if i.is_featured)
        public_categories.append(
            PublicCategory(
                id=category.id,
                name=category.name,
                description=category.description,
                image_url=category.image_url,
                icon=category.icon,
                translations=category.translations,
                items=public_items,
            )
        )

    return PublicMenuResponse(
        restaurant=PublicRestaurant.model_validate(restaurant),
        categories=public_categories,
        featured=featured,
    )
