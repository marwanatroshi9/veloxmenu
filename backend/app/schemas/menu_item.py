from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.menu_item import SpicyLevel
from app.schemas.translation import Translations, parse_translations


class MenuItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=512)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    category_id: int
    is_available: bool = True
    is_featured: bool = False
    preparation_time: int | None = Field(default=None, ge=0, le=1440)
    calories: int | None = Field(default=None, ge=0, le=100000)
    spicy_level: SpicyLevel = SpicyLevel.NONE
    ingredients: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    translations: Translations = Field(default_factory=dict)
    sort_order: int = 0

    @field_validator("ingredients", "tags")
    @classmethod
    def _limit_list(cls, v: list[str]) -> list[str]:
        cleaned = [s.strip() for s in v if s and s.strip()]
        if len(cleaned) > 50:
            raise ValueError("Too many entries (max 50)")
        return cleaned

    @field_validator("translations", mode="before")
    @classmethod
    def _parse_tr(cls, v: object) -> Translations:
        return parse_translations(v)

    @model_validator(mode="after")
    def _check_discount(self) -> "MenuItemBase":
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("discount_price must be lower than price")
        return self


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=512)
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    category_id: int | None = None
    is_available: bool | None = None
    is_featured: bool | None = None
    preparation_time: int | None = Field(default=None, ge=0, le=1440)
    calories: int | None = Field(default=None, ge=0, le=100000)
    spicy_level: SpicyLevel | None = None
    ingredients: list[str] | None = None
    tags: list[str] | None = None
    translations: Translations | None = None
    sort_order: int | None = None

    @field_validator("translations", mode="before")
    @classmethod
    def _parse_tr(cls, v: object) -> Translations | None:
        return None if v is None else parse_translations(v)


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    category_id: int
    name: str
    description: str | None
    image_url: str | None
    price: Decimal
    discount_price: Decimal | None
    is_available: bool
    is_featured: bool
    preparation_time: int | None
    calories: int | None
    spicy_level: SpicyLevel
    ingredients: list[str]
    tags: list[str]
    translations: Translations = Field(default_factory=dict)
    sort_order: int
    created_at: datetime

    @field_validator("ingredients", "tags", mode="before")
    @classmethod
    def _parse_json_list(cls, v: object) -> list[str]:
        import json

        if v is None:
            return []
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
