from __future__ import annotations

from pydantic import BaseModel

from app.models.subscription import SubscriptionPlan, SubscriptionStatus


class SuperAdminStats(BaseModel):
    total_restaurants: int
    active_restaurants: int
    suspended_restaurants: int
    total_menu_items: int
    total_categories: int
    total_managers: int
    active_subscriptions: int
    storage_bytes: int


class RestaurantStats(BaseModel):
    total_categories: int
    visible_categories: int
    total_menu_items: int
    available_items: int
    featured_items: int
    storage_bytes: int


class SubscriptionOut(BaseModel):
    plan: SubscriptionPlan
    status: SubscriptionStatus
    current_period_end: str | None = None


class SubscriptionUpdate(BaseModel):
    plan: SubscriptionPlan | None = None
    status: SubscriptionStatus | None = None
