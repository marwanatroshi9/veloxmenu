"""Cloudinary image upload service.

Applies automatic compression (quality:auto), format conversion (fetch_format:auto
=> WebP/AVIF where supported) and server-side resizing. When Cloudinary is not
configured, uploads raise a clear error so callers can surface a 503.
"""
from __future__ import annotations

from typing import Any

from fastapi import UploadFile

from app.core.config import settings

if settings.cloudinary_enabled:  # pragma: no cover - depends on env
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/avif"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB


class CloudinaryError(RuntimeError):
    pass


# Named transformation presets per purpose.
_TRANSFORMS: dict[str, dict[str, Any]] = {
    "logo": {"width": 512, "height": 512, "crop": "limit"},
    "cover": {"width": 1920, "height": 1080, "crop": "limit"},
    "category": {"width": 1024, "height": 1024, "crop": "limit"},
    "item": {"width": 1200, "height": 1200, "crop": "limit"},
}


async def upload_image(
    file: UploadFile,
    *,
    purpose: str,
    folder_suffix: str,
) -> dict[str, Any]:
    """Validate and upload an image. Returns Cloudinary result dict."""
    if not settings.cloudinary_enabled:
        raise CloudinaryError("Image storage is not configured")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise CloudinaryError("Unsupported image type")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise CloudinaryError("Image exceeds 8 MB limit")

    transform = _TRANSFORMS.get(purpose, _TRANSFORMS["item"])
    result = cloudinary.uploader.upload(  # type: ignore[union-attr]
        data,
        folder=f"{settings.CLOUDINARY_FOLDER}/{folder_suffix}",
        resource_type="image",
        transformation=[{**transform, "quality": "auto", "fetch_format": "auto"}],
        overwrite=True,
        invalidate=True,
    )
    return result


def delete_image(public_id: str) -> None:
    if not settings.cloudinary_enabled:
        return
    cloudinary.uploader.destroy(public_id, invalidate=True)  # type: ignore[union-attr]
