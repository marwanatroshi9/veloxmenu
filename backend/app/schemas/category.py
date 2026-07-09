from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.translation import Translations, parse_translations


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=512)
    icon: str | None = Field(default=None, max_length=40)
    translations: Translations = Field(default_factory=dict)
    is_visible: bool = True
    sort_order: int = 0

    @field_validator("translations", mode="before")
    @classmethod
    def _parse_tr(cls, v: object) -> Translations:
        return parse_translations(v)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=512)
    icon: str | None = Field(default=None, max_length=40)
    translations: Translations | None = None
    is_visible: bool | None = None
    sort_order: int | None = None

    @field_validator("translations", mode="before")
    @classmethod
    def _parse_tr(cls, v: object) -> Translations | None:
        return None if v is None else parse_translations(v)


class CategoryReorderItem(BaseModel):
    id: int
    sort_order: int


class CategoryReorder(BaseModel):
    items: list[CategoryReorderItem]


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    image_url: str | None
    created_at: datetime
