"""Storage facade: use Cloudinary when configured, otherwise local disk.

Endpoints import `upload_image` / `delete_image` / `CloudinaryError` from here and
stay agnostic to the backend. Both implementations return the same result shape:
{"secure_url": str, "public_id": str, "bytes": int}.
"""
from __future__ import annotations

from fastapi import UploadFile

from app.core.config import settings
from app.services.cloudinary_service import CloudinaryError
from app.services.cloudinary_service import delete_image as _cloud_delete
from app.services.cloudinary_service import upload_image as _cloud_upload
from app.services.local_storage import delete_image_local, save_image_local

__all__ = ["upload_image", "delete_image", "CloudinaryError"]


async def upload_image(file: UploadFile, *, purpose: str, folder_suffix: str) -> dict:
    if settings.cloudinary_enabled:
        return await _cloud_upload(file, purpose=purpose, folder_suffix=folder_suffix)
    return await save_image_local(file, purpose=purpose, folder_suffix=folder_suffix)


def delete_image(public_id: str) -> None:
    if settings.cloudinary_enabled:
        _cloud_delete(public_id)
    else:
        delete_image_local(public_id)
