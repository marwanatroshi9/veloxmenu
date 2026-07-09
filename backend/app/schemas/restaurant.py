from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from app.models.restaurant import RestaurantStatus


# --- Profile (editable by restaurant manager) --------------------------------
class RestaurantProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    theme_color: str | None = Field(default=None, pattern=r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
    phone: str | None = Field(default=None, max_length=40)
    whatsapp: str | None = Field(default=None, max_length=40)
    instagram: str | None = Field(default=None, max_length=255)
    facebook: str | None = Field(default=None, max_length=255)
    tiktok: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=512)
    google_maps_url: str | None = Field(default=None, max_length=512)
    opening_hours: str | None = None  # JSON string
    currency: str | None = Field(default=None, max_length=8)
    default_language: str | None = Field(default=None, max_length=8)


# --- Super-admin create/update ----------------------------------------------
class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    # Manager to create and assign to this restaurant.
    manager_email: EmailStr
    manager_password: str = Field(min_length=8, max_length=128)
    manager_full_name: str | None = Field(default=None, max_length=255)


class RestaurantAdminUpdate(RestaurantProfileUpdate):
    slug: str | None = Field(default=None, max_length=255)
    status: RestaurantStatus | None = None


# --- Output ------------------------------------------------------------------
class RestaurantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    status: RestaurantStatus
    description: str | None
    logo_url: str | None
    cover_url: str | None
    theme_color: str
    phone: str | None
    whatsapp: str | None
    instagram: str | None
    facebook: str | None
    tiktok: str | None
    website: str | None
    address: str | None
    google_maps_url: str | None
    opening_hours: str | None
    currency: str
    default_language: str
    created_at: datetime


class RestaurantSummary(BaseModel):
    """Lightweight row for admin list tables."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    status: RestaurantStatus
    logo_url: str | None
    created_at: datetime


class ResetPasswordResponse(BaseModel):
    manager_email: EmailStr
    temporary_password: str
