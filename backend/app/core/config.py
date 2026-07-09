"""Application configuration loaded from environment variables.

All settings are validated at startup via pydantic-settings. Secrets must be
provided through the environment (see .env.example); no secret has a usable
default in production.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    PROJECT_NAME: str = "MenuHub"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # --- Security ---
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    # Cookie settings for refresh tokens
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_DOMAIN: str | None = None

    # --- CORS ---
    # Comma-separated list of allowed origins for the browser frontend.
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # --- Database ---
    DATABASE_URL: PostgresDsn

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    CLOUDINARY_FOLDER: str = "menuhub"

    # --- Public site ---
    PUBLIC_SITE_URL: str = "http://localhost:3000"

    # --- Rate limiting ---
    RATE_LIMIT_DEFAULT: str = "200/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # --- Bootstrap superadmin (used by seed script only) ---
    # Note: use a real, non-reserved domain — ".local" addresses are rejected by
    # email validation and cannot be used to log in.
    FIRST_SUPERADMIN_EMAIL: str = "admin@menuhub.app"
    FIRST_SUPERADMIN_PASSWORD: str = "ChangeMe123!"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _coerce_db_url(cls, v: str) -> str:
        # Ensure we use the psycopg (v3) driver.
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @property
    def cloudinary_enabled(self) -> bool:
        return all(
            [
                self.CLOUDINARY_CLOUD_NAME,
                self.CLOUDINARY_API_KEY,
                self.CLOUDINARY_API_SECRET,
            ]
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
