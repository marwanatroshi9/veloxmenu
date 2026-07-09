from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import SuperAdmin
from app.database.session import get_db
from app.models.category import Category
from app.models.media import Media
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant, RestaurantStatus
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User, UserRole
from app.schemas.dashboard import SuperAdminStats

router = APIRouter(prefix="/admin", tags=["admin:dashboard"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/stats", response_model=SuperAdminStats)
def super_admin_stats(admin: SuperAdmin, db: DbSession):
    total_restaurants = db.scalar(select(func.count(Restaurant.id))) or 0
    active = db.scalar(
        select(func.count(Restaurant.id)).where(Restaurant.status == RestaurantStatus.ACTIVE)
    ) or 0
    suspended = db.scalar(
        select(func.count(Restaurant.id)).where(Restaurant.status == RestaurantStatus.SUSPENDED)
    ) or 0
    total_items = db.scalar(select(func.count(MenuItem.id))) or 0
    total_categories = db.scalar(select(func.count(Category.id))) or 0
    total_managers = db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.RESTAURANT_MANAGER)
    ) or 0
    active_subs = db.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    ) or 0
    storage = db.scalar(select(func.coalesce(func.sum(Media.bytes), 0))) or 0

    return SuperAdminStats(
        total_restaurants=total_restaurants,
        active_restaurants=active,
        suspended_restaurants=suspended,
        total_menu_items=total_items,
        total_categories=total_categories,
        total_managers=total_managers,
        active_subscriptions=active_subs,
        storage_bytes=int(storage),
    )
