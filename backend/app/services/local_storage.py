"""Local disk image storage — used when Cloudinary is not configured.

Uploads are validated, auto-oriented, resized to a sane maximum per purpose, and
written as WebP into UPLOAD_DIR. The returned dict mirrors the Cloudinary result
shape (secure_url / public_id / bytes) so callers are storage-agnostic. Files are
served back at MEDIA_URL_PREFIX by the backend (proxied through nginx).
"""
from __future__ import annotations

import io
import os
import uuid

from fastapi import UploadFile
from PIL import Image, ImageOps

from app.core.config import settings
from app.services.cloudinary_service import (
    ALLOWED_CONTENT_TYPES,
    MAX_UPLOAD_BYTES,
    CloudinaryError,
)

# Max (width, height) per image purpose; images are only ever scaled down.
_MAX_SIZE: dict[str, tuple[int, int]] = {
    "logo": (512, 512),
    "cover": (1920, 1080),
    "category": (1024, 1024),
    "item": (1200, 1200),
}


async def save_image_local(
    file: UploadFile, *, purpose: str, folder_suffix: str
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise CloudinaryError("Unsupported image type")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise CloudinaryError("Image exceeds 8 MB limit")

    try:
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img)  # respect camera orientation
    except Exception as exc:  # noqa: BLE001
        raise CloudinaryError("Invalid image file") from exc

    max_w, max_h = _MAX_SIZE.get(purpose, (1200, 1200))
    img.thumbnail((max_w, max_h))

    # WebP keeps transparency (logos) and compresses well.
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

    rel_dir = folder_suffix.strip("/")
    abs_dir = os.path.join(settings.UPLOAD_DIR, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.webp"
    abs_path = os.path.join(abs_dir, filename)
    img.save(abs_path, "WEBP", quality=82, method=6)

    public_id = f"{rel_dir}/{filename}"
    url = f"{settings.MEDIA_URL_PREFIX}/{public_id}"
    return {"secure_url": url, "public_id": public_id, "bytes": os.path.getsize(abs_path)}


def delete_image_local(public_id: str) -> None:
    if not public_id:
        return
    abs_path = os.path.join(settings.UPLOAD_DIR, public_id)
    try:
        if os.path.commonpath([os.path.abspath(abs_path), os.path.abspath(settings.UPLOAD_DIR)]) == os.path.abspath(settings.UPLOAD_DIR):
            os.remove(abs_path)
    except (OSError, ValueError):
        pass
