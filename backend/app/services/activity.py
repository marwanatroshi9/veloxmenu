from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    *,
    action: str,
    user_id: int | None = None,
    restaurant_id: int | None = None,
    entity_type: str | None = None,
    entity_id: str | int | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
    commit: bool = True,
) -> ActivityLog:
    """Append an entry to the audit log."""
    entry = ActivityLog(
        action=action,
        user_id=user_id,
        restaurant_id=restaurant_id,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry
