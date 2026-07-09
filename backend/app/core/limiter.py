"""Rate limiting.

- A global default limit is applied to every request via SlowAPIMiddleware.
- Sensitive auth routes get a stricter limit through the `auth_rate_limit`
  dependency, which uses the `limits` library directly (avoids the FastAPI
  signature issues of the slowapi route decorator).
"""
from __future__ import annotations

from fastapi import HTTPException, Request, status
from limits import parse
from limits.storage import storage_from_string
from limits.strategies import MovingWindowRateLimiter
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Used by SlowAPIMiddleware for the global default limit.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    headers_enabled=True,
)

# Dedicated limiter for auth endpoints.
_auth_storage = storage_from_string("memory://")
_auth_strategy = MovingWindowRateLimiter(_auth_storage)
_auth_limit = parse(settings.RATE_LIMIT_AUTH)


def auth_rate_limit(request: Request) -> None:
    identifier = get_remote_address(request)
    if not _auth_strategy.hit(_auth_limit, "auth", identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please slow down.",
        )
