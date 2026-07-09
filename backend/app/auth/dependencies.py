"""FastAPI security dependencies enforcing authentication and tenant isolation."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import JWTError, decode_access_token
from app.database.session import get_db
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = db.get(User, int(user_id)) if user_id else None
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_super_admin(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required",
        )
    return current_user


def get_current_restaurant(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Restaurant:
    """Resolve and return the restaurant the current manager owns.

    This is THE tenant-isolation boundary: every restaurant-scoped route depends
    on this, and all queries are filtered by the returned restaurant's id. A
    manager can never reference another tenant's id because it is derived from
    their own token, not from request input.
    """
    if current_user.role != UserRole.RESTAURANT_MANAGER or current_user.restaurant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant manager account required",
        )
    restaurant = db.get(Restaurant, current_user.restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    if not restaurant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Restaurant is suspended"
        )
    return restaurant


SuperAdmin = Annotated[User, Depends(require_super_admin)]
CurrentRestaurant = Annotated[Restaurant, Depends(get_current_restaurant)]
