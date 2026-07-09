from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    admin_dashboard,
    admin_restaurants,
    auth,
    categories,
    menu_items,
    profile,
    public,
    qrcode,
    restaurant_dashboard,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin_dashboard.router)
api_router.include_router(admin_restaurants.router)
api_router.include_router(profile.router)
api_router.include_router(restaurant_dashboard.router)
api_router.include_router(categories.router)
api_router.include_router(menu_items.router)
api_router.include_router(qrcode.router)
api_router.include_router(public.router)
