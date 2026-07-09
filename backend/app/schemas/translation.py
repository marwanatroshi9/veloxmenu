from __future__ import annotations

import json

from pydantic import BaseModel, Field, field_validator

# Supported non-default languages for content translations.
SUPPORTED_LANGUAGES = ("ar", "ckb")


class TranslatedText(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None


# Map of language code -> translated fields.
Translations = dict[str, TranslatedText]


def parse_translations(value: object) -> Translations:
    """Coerce a stored JSON string (or dict) into a Translations map."""
    if value is None:
        return {}
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return {}
    if not isinstance(value, dict):
        return {}
    out: Translations = {}
    for lang, fields in value.items():
        if isinstance(fields, dict):
            out[lang] = TranslatedText(
                name=fields.get("name"), description=fields.get("description")
            )
    return out


def dump_translations(translations: Translations | None) -> str:
    """Serialize a Translations map to a compact JSON string for storage."""
    if not translations:
        return "{}"
    payload = {
        lang: {"name": t.name, "description": t.description}
        for lang, t in translations.items()
        if t.name or t.description
    }
    return json.dumps(payload, ensure_ascii=False)


class TranslationsField(BaseModel):
    """Mixin providing a validated `translations` field with JSON parsing."""

    translations: Translations = Field(default_factory=dict)

    @field_validator("translations", mode="before")
    @classmethod
    def _parse(cls, v: object) -> Translations:
        return parse_translations(v)
