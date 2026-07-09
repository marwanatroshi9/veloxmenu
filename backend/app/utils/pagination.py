from __future__ import annotations

from math import ceil
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.common import PageMeta


def paginate(
    db: Session,
    stmt: Select[Any],
    *,
    page: int,
    page_size: int,
) -> tuple[list[Any], PageMeta]:
    """Execute a SELECT with LIMIT/OFFSET and return rows plus page metadata."""
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    rows = list(
        db.scalars(stmt.limit(page_size).offset((page - 1) * page_size)).all()
    )
    meta = PageMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if page_size else 1,
    )
    return rows, meta
