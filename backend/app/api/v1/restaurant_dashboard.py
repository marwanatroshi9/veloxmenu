from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentRestaurant
from app.database.session import get_db
from app.models.category import Category
from app.models.media import Media
from app.models.menu_item import MenuItem
from app.schemas.dashboard import RestaurantStats

router = APIRouter(prefix="/restaurant", tags=["restaurant:dashboard"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/stats", response_model=RestaurantStats)
def restaurant_stats(restaurant: CurrentRestaurant, db: DbSession):
    rid = restaurant.id
    total_categories = db.scalar(
        select(func.count(Category.id)).where(Category.restaurant_id == rid)
    ) or 0
    visible_categories = db.scalar(
        select(func.count(Category.id)).where(
            Category.restaurant_id == rid, Category.is_visible.is_(True)
        )
    ) or 0
    total_items = db.scalar(
        select(func.count(MenuItem.id)).where(MenuItem.restaurant_id == rid)
    ) or 0
    available_items = db.scalar(
        select(func.count(MenuItem.id)).where(
            MenuItem.restaurant_id == rid, MenuItem.is_available.is_(True)
        )
    ) or 0
    featured_items = db.scalar(
        select(func.count(MenuItem.id)).where(
            MenuItem.restaurant_id == rid, MenuItem.is_featured.is_(True)
        )
    ) or 0
    storage = db.scalar(
        select(func.coalesce(func.sum(Media.bytes), 0)).where(Media.restaurant_id == rid)
    ) or 0

    return RestaurantStats(
        total_categories=total_categories,
        visible_categories=visible_categories,
        total_menu_items=total_items,
        available_items=available_items,
        featured_items=featured_items,
        storage_bytes=int(storage),
    )
