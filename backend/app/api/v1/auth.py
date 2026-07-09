from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.cookies import clear_refresh_cookie, set_refresh_cookie
from app.auth.dependencies import CurrentUser
from app.auth.service import (
    authenticate_user,
    issue_access_token,
    issue_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.core.limiter import auth_rate_limit
from app.core.security import hash_password, verify_password
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangeEmailRequest,
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
)
from app.schemas.common import Message
from app.schemas.user import UserOut
from app.services.activity import log_activity

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(auth_rate_limit)])
def login(request: Request, payload: LoginRequest, response: Response, db: DbSession):
    user = authenticate_user(db, payload.email, payload.password)
    access_token, expires_in = issue_access_token(user)
    raw_refresh = issue_refresh_token(
        db,
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    set_refresh_cookie(response, raw_refresh)
    log_activity(
        db,
        action="auth.login",
        user_id=user.id,
        restaurant_id=user.restaurant_id,
        ip_address=request.client.host if request.client else None,
    )
    return TokenResponse(access_token=access_token, expires_in=expires_in)


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(auth_rate_limit)])
def refresh(
    request: Request,
    response: Response,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    user, new_raw = rotate_refresh_token(
        db,
        refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    access_token, expires_in = issue_access_token(user)
    set_refresh_cookie(response, new_raw)
    return TokenResponse(access_token=access_token, expires_in=expires_in)


@router.post("/logout", response_model=Message)
def logout(
    response: Response,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if refresh_token:
        revoke_refresh_token(db, refresh_token)
    clear_refresh_cookie(response)
    return Message(detail="Logged out")


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser):
    return current_user


@router.post("/change-password", response_model=Message)
def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DbSession,
    request: Request,
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    log_activity(
        db,
        action="auth.change_password",
        user_id=current_user.id,
        restaurant_id=current_user.restaurant_id,
        ip_address=request.client.host if request.client else None,
    )
    return Message(detail="Password updated")


@router.post("/change-email", response_model=UserOut)
def change_email(
    payload: ChangeEmailRequest,
    current_user: CurrentUser,
    db: DbSession,
    request: Request,
):
    # Re-authenticate with the current password before allowing an email change.
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    new_email = payload.new_email.lower()
    if new_email != current_user.email:
        taken = db.scalar(
            select(User.id).where(User.email == new_email, User.id != current_user.id)
        )
        if taken is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email is already in use"
            )
        current_user.email = new_email
        db.commit()
        db.refresh(current_user)
        log_activity(
            db,
            action="auth.change_email",
            user_id=current_user.id,
            restaurant_id=current_user.restaurant_id,
            ip_address=request.client.host if request.client else None,
        )
    return current_user
