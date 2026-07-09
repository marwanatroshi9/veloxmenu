from __future__ import annotations

import io
from typing import Annotated, Literal

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentRestaurant
from app.core.config import settings
from app.database.session import get_db
from app.models.restaurant import Restaurant

router = APIRouter(prefix="/restaurant/qrcode", tags=["restaurant:qrcode"])

DbSession = Annotated[Session, Depends(get_db)]


def _public_url(restaurant: Restaurant) -> str:
    return f"{settings.PUBLIC_SITE_URL.rstrip('/')}/{restaurant.slug}"


def _png_bytes(data: str) -> bytes:
    qr = qrcode.QRCode(version=None, box_size=12, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _svg_bytes(data: str) -> bytes:
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(data, image_factory=factory, border=2)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue()


@router.get("")
def get_qrcode(
    restaurant: CurrentRestaurant,
    db: DbSession,
    fmt: Literal["png", "svg", "pdf"] = Query("png", alias="format"),
):
    url = _public_url(restaurant)
    filename = f"{restaurant.slug}-qr"

    if fmt == "png":
        return Response(
            content=_png_bytes(url),
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{filename}.png"'},
        )
    if fmt == "svg":
        return Response(
            content=_svg_bytes(url),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}.svg"'},
        )
    # PDF: embed the PNG QR into a single-page document.
    try:
        from reportlab.lib.pagesizes import A6  # type: ignore
        from reportlab.lib.units import mm  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
        from reportlab.lib.utils import ImageReader  # type: ignore
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF export requires the reportlab package",
        )
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A6)
    width, height = A6
    qr_img = ImageReader(io.BytesIO(_png_bytes(url)))
    size = 80 * mm
    c.drawImage(qr_img, (width - size) / 2, (height - size) / 2, size, size)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 20 * mm, restaurant.name)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 15 * mm, url)
    c.showPage()
    c.save()
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'},
    )
