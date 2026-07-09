from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentRestaurant
from app.database.session import get_db
from app.models.media import Media
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantOut, RestaurantProfileUpdate
from app.services.storage import CloudinaryError, upload_image

router = APIRouter(prefix="/restaurant", tags=["restaurant:profile"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/profile", response_model=RestaurantOut)
def get_profile(restaurant: CurrentRestaurant):
    return restaurant


@router.patch("/profile", response_model=RestaurantOut)
def update_profile(
    payload: RestaurantProfileUpdate, restaurant: CurrentRestaurant, db: DbSession
):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


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


@router.post("/logo", response_model=RestaurantOut)
async def upload_logo(restaurant: CurrentRestaurant, db: DbSession, file: UploadFile):
    return await _upload_branding(db, restaurant, file, "logo")


@router.post("/cover", response_model=RestaurantOut)
async def upload_cover(restaurant: CurrentRestaurant, db: DbSession, file: UploadFile):
    return await _upload_branding(db, restaurant, file, "cover")
