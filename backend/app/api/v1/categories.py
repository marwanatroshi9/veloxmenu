from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentRestaurant
from app.database.session import get_db
from app.models.category import Category
from app.models.media import Media
from app.models.restaurant import Restaurant
from app.schemas.category import (
    CategoryCreate,
    CategoryOut,
    CategoryReorder,
    CategoryUpdate,
)
from app.schemas.common import Message
from app.services.storage import CloudinaryError, upload_image

router = APIRouter(prefix="/restaurant/categories", tags=["restaurant:categories"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_owned(db: Session, restaurant: Restaurant, category_id: int) -> Category:
    """Fetch a category, enforcing it belongs to the caller's restaurant."""
    category = db.get(Category, category_id)
    if category is None or category.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(restaurant: CurrentRestaurant, db: DbSession):
    rows = db.scalars(
        select(Category)
        .where(Category.restaurant_id == restaurant.id)
        .order_by(Category.sort_order.asc(), Category.id.asc())
    ).all()
    return list(rows)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, restaurant: CurrentRestaurant, db: DbSession):
    data = payload.model_dump()
    data["translations"] = json.dumps(data["translations"], ensure_ascii=False)
    category = Category(restaurant_id=restaurant.id, **data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/reorder", response_model=Message)
def reorder_categories(payload: CategoryReorder, restaurant: CurrentRestaurant, db: DbSession):
    ids = [i.id for i in payload.items]
    owned = db.scalars(
        select(Category).where(
            Category.restaurant_id == restaurant.id, Category.id.in_(ids)
        )
    ).all()
    owned_map = {c.id: c for c in owned}
    if len(owned_map) != len(set(ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown category id")
    for item in payload.items:
        owned_map[item.id].sort_order = item.sort_order
    db.commit()
    return Message(detail="Reordered")


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int, payload: CategoryUpdate, restaurant: CurrentRestaurant, db: DbSession
):
    category = _get_owned(db, restaurant, category_id)
    data = payload.model_dump(exclude_unset=True)
    if "translations" in data and data["translations"] is not None:
        data["translations"] = json.dumps(data["translations"], ensure_ascii=False)
    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=Message)
def delete_category(category_id: int, restaurant: CurrentRestaurant, db: DbSession):
    category = _get_owned(db, restaurant, category_id)
    db.delete(category)
    db.commit()
    return Message(detail="Category deleted")


@router.post("/{category_id}/image", response_model=CategoryOut)
async def upload_category_image(
    category_id: int, restaurant: CurrentRestaurant, db: DbSession, file: UploadFile
):
    category = _get_owned(db, restaurant, category_id)
    try:
        result = await upload_image(
            file, purpose="category", folder_suffix=f"r{restaurant.id}/categories"
        )
    except CloudinaryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    category.image_url = result["secure_url"]
    db.add(
        Media(
            restaurant_id=restaurant.id,
            public_id=result["public_id"],
            url=result["secure_url"],
            bytes=result.get("bytes", 0),
            purpose="category",
        )
    )
    db.commit()
    db.refresh(category)
    return category
