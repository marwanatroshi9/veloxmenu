from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import SuperAdmin
from app.core.security import hash_password
from app.database.session import get_db
from app.models.category import Category
from app.models.media import Media
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant, RestaurantStatus
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User, UserRole
from app.schemas.common import Message, Page, PageMeta
from app.schemas.dashboard import (
    SubscriptionOut,
    SubscriptionUpdate,
    SuperAdminStats,
)
from app.schemas.restaurant import (
    RestaurantAdminUpdate,
    RestaurantCreate,
    RestaurantOut,
    RestaurantSummary,
    ResetPasswordResponse,
)
from app.services.activity import log_activity
from app.services.storage import CloudinaryError, upload_image
from app.utils.pagination import paginate
from app.utils.slug import unique_restaurant_slug

router = APIRouter(prefix="/admin/restaurants", tags=["admin:restaurants"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_or_404(db: Session, restaurant_id: int) -> Restaurant:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant


@router.get("", response_model=Page[RestaurantSummary])
def list_restaurants(
    admin: SuperAdmin,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    status_filter: RestaurantStatus | None = Query(None, alias="status"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    stmt = select(Restaurant)
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(func.lower(Restaurant.name).like(like))
    if status_filter:
        stmt = stmt.where(Restaurant.status == status_filter)

    sort_col = {
        "name": Restaurant.name,
        "created_at": Restaurant.created_at,
    }.get(sort_by, Restaurant.created_at)
    stmt = stmt.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    rows, meta = paginate(db, stmt, page=page, page_size=page_size)
    return Page[RestaurantSummary](
        items=[RestaurantSummary.model_validate(r) for r in rows], meta=meta
    )


@router.post("", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
def create_restaurant(payload: RestaurantCreate, admin: SuperAdmin, db: DbSession, request: Request):
    if db.scalar(select(User.id).where(User.email == payload.manager_email.lower())):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Manager email already in use"
        )

    slug = unique_restaurant_slug(db, payload.name, payload.slug)
    restaurant = Restaurant(name=payload.name, slug=slug, description=payload.description)
    db.add(restaurant)
    db.flush()  # obtain restaurant.id

    manager = User(
        email=payload.manager_email.lower(),
        hashed_password=hash_password(payload.manager_password),
        full_name=payload.manager_full_name,
        role=UserRole.RESTAURANT_MANAGER,
        restaurant_id=restaurant.id,
    )
    db.add(manager)
    db.add(Subscription(restaurant_id=restaurant.id))
    db.commit()
    db.refresh(restaurant)

    log_activity(
        db,
        action="restaurant.create",
        user_id=admin.id,
        restaurant_id=restaurant.id,
        entity_type="restaurant",
        entity_id=restaurant.id,
        ip_address=request.client.host if request.client else None,
    )
    return restaurant


@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: int, admin: SuperAdmin, db: DbSession):
    return _get_or_404(db, restaurant_id)


@router.patch("/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(
    restaurant_id: int, payload: RestaurantAdminUpdate, admin: SuperAdmin, db: DbSession
):
    restaurant = _get_or_404(db, restaurant_id)
    data = payload.model_dump(exclude_unset=True)
    if "slug" in data and data["slug"]:
        data["slug"] = unique_restaurant_slug(db, restaurant.name, data["slug"])
    for key, value in data.items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}", response_model=Message)
def delete_restaurant(restaurant_id: int, admin: SuperAdmin, db: DbSession, request: Request):
    restaurant = _get_or_404(db, restaurant_id)
    db.delete(restaurant)
    db.commit()
    log_activity(
        db,
        action="restaurant.delete",
        user_id=admin.id,
        entity_type="restaurant",
        entity_id=restaurant_id,
        ip_address=request.client.host if request.client else None,
    )
    return Message(detail="Restaurant deleted")


@router.post("/{restaurant_id}/suspend", response_model=RestaurantOut)
def suspend_restaurant(restaurant_id: int, admin: SuperAdmin, db: DbSession):
    restaurant = _get_or_404(db, restaurant_id)
    restaurant.status = RestaurantStatus.SUSPENDED
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.post("/{restaurant_id}/activate", response_model=RestaurantOut)
def activate_restaurant(restaurant_id: int, admin: SuperAdmin, db: DbSession):
    restaurant = _get_or_404(db, restaurant_id)
    restaurant.status = RestaurantStatus.ACTIVE
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.post("/{restaurant_id}/reset-manager-password", response_model=ResetPasswordResponse)
def reset_manager_password(restaurant_id: int, admin: SuperAdmin, db: DbSession):
    restaurant = _get_or_404(db, restaurant_id)
    manager = db.scalar(
        select(User).where(
            User.restaurant_id == restaurant.id, User.role == UserRole.RESTAURANT_MANAGER
        )
    )
    if manager is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found")
    temp_password = secrets.token_urlsafe(12)
    manager.hashed_password = hash_password(temp_password)
    db.commit()
    return ResetPasswordResponse(manager_email=manager.email, temporary_password=temp_password)


@router.get("/{restaurant_id}/subscription", response_model=SubscriptionOut)
def get_subscription(restaurant_id: int, admin: SuperAdmin, db: DbSession):
    restaurant = _get_or_404(db, restaurant_id)
    sub = restaurant.subscription
    if sub is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subscription")
    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
    )


@router.patch("/{restaurant_id}/subscription", response_model=SubscriptionOut)
def update_subscription(
    restaurant_id: int, payload: SubscriptionUpdate, admin: SuperAdmin, db: DbSession
):
    restaurant = _get_or_404(db, restaurant_id)
    sub = restaurant.subscription or Subscription(restaurant_id=restaurant.id)
    if payload.plan is not None:
        sub.plan = payload.plan
    if payload.status is not None:
        sub.status = payload.status
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
    )


async def _upload_branding(
    db: Session, restaurant: Restaurant, file: UploadFile, purpose: str
) -> Restaurant:
    try:
        result = await upload_image(file, purpose=purpose, folder_suffix=f"r{restaurant.id}")
    except CloudinaryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    url = result["secure_url"]
    if purpose == "logo":
        restaurant.logo_url = url
    else:
        restaurant.cover_url = url
    db.add(
        Media(
            restaurant_id=restaurant.id,
            public_id=result["public_id"],
            url=url,
            bytes=result.get("bytes", 0),
            purpose=purpose,
        )
    )
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.post("/{restaurant_id}/logo", response_model=RestaurantOut)
async def upload_logo(restaurant_id: int, admin: SuperAdmin, db: DbSession, file: UploadFile):
    restaurant = _get_or_404(db, restaurant_id)
    return await _upload_branding(db, restaurant, file, "logo")


@router.post("/{restaurant_id}/cover", response_model=RestaurantOut)
async def upload_cover(restaurant_id: int, admin: SuperAdmin, db: DbSession, file: UploadFile):
    restaurant = _get_or_404(db, restaurant_id)
    return await _upload_branding(db, restaurant, file, "cover")
