from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.menu_item import SpicyLevel
from app.schemas.translation import Translations, parse_translations


class PublicMenuItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    image_url: str | None
    price: Decimal
    discount_price: Decimal | None
    is_featured: bool
    preparation_time: int | None
    calories: int | None
    spicy_level: SpicyLevel
    ingredients: list[str]
    tags: list[str]
    translations: Translations = Field(default_factory=dict)

    @field_validator("ingredients", "tags", mode="before")
    @classmethod
    def _parse_json_list(cls, v: object) -> list[str]:
        import json

        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
        return []

    @field_validator("translations", mode="before")
    @classmethod
    def _parse_tr(cls, v: object) -> Translations:
        return parse_translations(v)


class PublicCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    image_url: str | None
    icon: str | None = None
    translations: Translations = Field(default_factory=dict)
    items: list[PublicMenuItem] = []

    @field_validator("translations", mode="before")
    @classmethod
    def _parse_tr(cls, v: object) -> Translations:
        return parse_translations(v)


class PublicRestaurant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
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


class PublicMenuResponse(BaseModel):
    restaurant: PublicRestaurant
    categories: list[PublicCategory]
    featured: list[PublicMenuItem]
