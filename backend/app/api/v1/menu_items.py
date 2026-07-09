from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentRestaurant
from app.database.session import get_db
from app.models.category import Category
from app.models.media import Media
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.schemas.common import Message, Page
from app.schemas.menu_item import MenuItemCreate, MenuItemOut, MenuItemUpdate
from app.services.cloudinary_service import CloudinaryError, upload_image
from app.utils.pagination import paginate

router = APIRouter(prefix="/restaurant/menu-items", tags=["restaurant:menu-items"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_owned(db: Session, restaurant: Restaurant, item_id: int) -> MenuItem:
    item = db.get(MenuItem, item_id)
    if item is None or item.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return item


def _assert_category(db: Session, restaurant: Restaurant, category_id: int) -> None:
    cat = db.get(Category, category_id)
    if cat is None or cat.restaurant_id != restaurant.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not belong to restaurant"
        )


@router.get("", response_model=Page[MenuItemOut])
def list_menu_items(
    restaurant: CurrentRestaurant,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    category_id: int | None = Query(None),
    available: bool | None = Query(None),
    featured: bool | None = Query(None),
    sort_by: str = Query("sort_order"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
):
    stmt = select(MenuItem).where(MenuItem.restaurant_id == restaurant.id)
    if search:
        stmt = stmt.where(func.lower(MenuItem.name).like(f"%{search.lower()}%"))
    if category_id is not None:
        stmt = stmt.where(MenuItem.category_id == category_id)
    if available is not None:
        stmt = stmt.where(MenuItem.is_available.is_(available))
    if featured is not None:
        stmt = stmt.where(MenuItem.is_featured.is_(featured))

    sort_col = {
        "name": MenuItem.name,
        "price": MenuItem.price,
        "created_at": MenuItem.created_at,
        "sort_order": MenuItem.sort_order,
    }.get(sort_by, MenuItem.sort_order)
    stmt = stmt.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    rows, meta = paginate(db, stmt, page=page, page_size=page_size)
    return Page[MenuItemOut](items=[MenuItemOut.model_validate(r) for r in rows], meta=meta)


@router.post("", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemCreate, restaurant: CurrentRestaurant, db: DbSession):
    _assert_category(db, restaurant, payload.category_id)
    data = payload.model_dump()
    data["ingredients"] = json.dumps(data["ingredients"])
    data["tags"] = json.dumps(data["tags"])
    data["translations"] = json.dumps(data["translations"], ensure_ascii=False)
    item = MenuItem(restaurant_id=restaurant.id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int, restaurant: CurrentRestaurant, db: DbSession):
    return _get_owned(db, restaurant, item_id)


@router.patch("/{item_id}", response_model=MenuItemOut)
def update_menu_item(
    item_id: int, payload: MenuItemUpdate, restaurant: CurrentRestaurant, db: DbSession
):
    item = _get_owned(db, restaurant, item_id)
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        _assert_category(db, restaurant, data["category_id"])
    if "ingredients" in data and data["ingredients"] is not None:
        data["ingredients"] = json.dumps(data["ingredients"])
    if "tags" in data and data["tags"] is not None:
        data["tags"] = json.dumps(data["tags"])
    if "translations" in data and data["translations"] is not None:
        data["translations"] = json.dumps(data["translations"], ensure_ascii=False)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=Message)
def delete_menu_item(item_id: int, restaurant: CurrentRestaurant, db: DbSession):
    item = _get_owned(db, restaurant, item_id)
    db.delete(item)
    db.commit()
    return Message(detail="Menu item deleted")


@router.post("/{item_id}/duplicate", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def duplicate_menu_item(item_id: int, restaurant: CurrentRestaurant, db: DbSession):
    item = _get_owned(db, restaurant, item_id)
    clone = MenuItem(
        restaurant_id=restaurant.id,
        category_id=item.category_id,
        name=f"{item.name} (Copy)",
        description=item.description,
        image_url=item.image_url,
        price=item.price,
        discount_price=item.discount_price,
        is_available=item.is_available,
        is_featured=False,
        preparation_time=item.preparation_time,
        calories=item.calories,
        spicy_level=item.spicy_level,
        ingredients=item.ingredients,
        tags=item.tags,
        translations=item.translations,
        sort_order=item.sort_order + 1,
    )
    db.add(clone)
    db.commit()
    db.refresh(clone)
    return clone


@router.post("/{item_id}/image", response_model=MenuItemOut)
async def upload_item_image(
    item_id: int, restaurant: CurrentRestaurant, db: DbSession, file: UploadFile
):
    item = _get_owned(db, restaurant, item_id)
    try:
        result = await upload_image(
            file, purpose="item", folder_suffix=f"r{restaurant.id}/items"
        )
    except CloudinaryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    item.image_url = result["secure_url"]
    db.add(
        Media(
            restaurant_id=restaurant.id,
            public_id=result["public_id"],
            url=result["secure_url"],
            bytes=result.get("bytes", 0),
            purpose="item",
        )
    )
    db.commit()
    db.refresh(item)
    return item
