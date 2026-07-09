"""Authentication service: login, token issuance, and refresh-token rotation.

Security properties:
- Passwords verified with bcrypt (constant-time compare inside passlib).
- Access tokens are short-lived JWTs; refresh tokens are opaque and stored hashed.
- Refresh rotation: each refresh consumes the presented token and issues a new one.
- Reuse detection: presenting an already-revoked token revokes the entire token
  family for that user (a signal of theft).
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    # Always run a hash comparison to reduce user-enumeration timing differences.
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )
    # Managers of a suspended restaurant cannot log in to the dashboard.
    if user.restaurant is not None and not user.restaurant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant is suspended",
        )
    return user


def issue_access_token(user: User) -> tuple[str, int]:
    token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        restaurant_id=user.restaurant_id,
    )
    return token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def issue_refresh_token(
    db: Session,
    user: User,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> str:
    raw = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw),
            expires_at=refresh_token_expiry(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
    )
    db.commit()
    return raw


def rotate_refresh_token(
    db: Session,
    raw_token: str,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str]:
    """Validate a refresh token, rotate it, and return (user, new_raw_token)."""
    token_hash = hash_refresh_token(raw_token)
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    now = datetime.now(timezone.utc)

    # Reuse detection: a revoked token being presented again => compromise.
    if record.revoked:
        _revoke_all_for_user(db, record.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected; session revoked",
        )

    if record.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    user = db.get(User, record.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable"
        )

    # Issue replacement and revoke the old one atomically.
    new_raw = generate_refresh_token()
    new_hash = hash_refresh_token(new_raw)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=refresh_token_expiry(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
    )
    record.revoked = True
    record.replaced_by = new_hash
    db.commit()
    return user, new_raw


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token_hash = hash_refresh_token(raw_token)
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .values(revoked=True)
    )
    db.commit()


def _revoke_all_for_user(db: Session, user_id: int) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    db.commit()
