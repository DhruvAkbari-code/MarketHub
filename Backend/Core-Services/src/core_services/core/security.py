import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status

from core_services.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt (12 rounds)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "utf-8"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_verification_token(user_id: uuid.UUID) -> str:
    return _create_token(
        str(user_id),
        "verify",
        timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
    )


def create_access_token(user_id: uuid.UUID) -> str:
    return _create_token(
        str(user_id), "access", timedelta(days=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    )


def decode_verification_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired. Please register again or request a new link.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification link",
        )

    if payload.get("type") != "verify":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token subject",
        )


def decode_access_token(token: str) -> uuid.UUID:
    """Return the user id from an access token, or raise 401"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token subject")


def create_password_reset_token(user_id: uuid.UUID) -> str:
    return _create_token(
        str(user_id),
        "password_reset",
        timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
    )


def decode_password_reset_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Password reset link has expired. Request a new one.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Invalid password reset link.",
        )

    if payload.get("type") != "password_reset":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Invalid token type.",
        )

    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Invalid token subject.",
        )
