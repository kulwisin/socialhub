from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.db.session import get_db

_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_access_token(user_id: str, email: str, exp_hours: int = 24) -> str:
    """Create a signed JWT for the given user."""
    expire = datetime.now(timezone.utc) + timedelta(hours=exp_hours)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises ValidationError if invalid or expired."""
    try:
        return jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[_ALGORITHM])
    except JWTError as exc:
        raise ValidationError(f"Invalid or expired token: {exc}") from exc


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> object:
    """
    FastAPI dependency that validates the Bearer JWT and returns the User row.
    Import the return type as User in callers to keep this module free of
    circular imports.
    """
    from app.models.user import User  # local import to avoid circular deps

    payload = decode_token(token)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise ValidationError("Token missing subject claim.")

    import uuid

    try:
        uid = uuid.UUID(user_id)
    except ValueError as exc:
        raise ValidationError("Token subject is not a valid UUID.") from exc

    user = await db.get(User, uid)
    if user is None:
        raise ValidationError("User not found.")
    if not user.is_active:
        raise ValidationError("User account is disabled.")
    return user
