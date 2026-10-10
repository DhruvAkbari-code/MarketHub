import re
import secrets
from datetime import datetime, timezone
from enum import Enum

from fastapi import HTTPException, status
from sqlmodel import Session, select

from core_api.models.user import User
from core_api.schemas.auth import RegisterRequest
from core_api.security import (
    verify_password,
    decode_verification_token,
    hash_password,
    create_access_token,
    decode_password_reset_token,
)
from core_api.models.user import Role
from core_api.services.google_service import verify_google_id_token


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def register_user(
    session: Session, data: RegisterRequest, role: Role = Role.customer
) -> User:
    email = str(data.email).strip().lower()

    existing_user = get_user_by_email(session, email)

    if existing_user is not None:
        if existing_user.google_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This email is already registered with Google. "
                    "Please sign in using Google."
                ),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email already exists. " "Please sign in instead."
            ),
        )

    user = User(
        email=data.email,
        username=data.username,
        phone=data.phone,
        role=role,
        password_hash=hash_password(data.password),
        email_verified=False,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def verify_email(session: Session, token: str) -> User:
    user_id = decode_verification_token(token)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if not user.email_verified:
        user.email_verified = True
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


def google_login(session: Session, raw_id_token: str) -> tuple[str, bool]:
    info = verify_google_id_token(raw_id_token)
    if not info.get("email_verified"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Google account email is not verified"
        )
    email = info["email"].lower()
    google_sub = info["sub"]
    picture = info.get("picture")
    display_name = info.get("name") or email.split("@")[0]

    user = get_user_by_email(session, email)
    is_new = False

    if user is not None:
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is disabled")
        if user.google_user_id and user.google_user_id != google_sub:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "This email is already linked to a different google account",
            )
        user.google_user_id = google_sub
        user.email_verified = True
        if picture and not user.profile_picture:
            user.profile_picture = picture
    else:
        is_new = True
        user = User(
            email=email,
            google_user_id=google_sub,
            username=display_name,
            profile_picture=picture,
            email_verified=True,
        )
    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)

    return create_access_token(user.id), is_new


def login_user(session: Session, email: str, password: str) -> User:
    email = email.strip().lower()
    user = get_user_by_email(session, email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is disabled. Please contact support.",
        )

    if not user.password_hash:
        if user.google_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses Google sign-in. Please sign in with Google.",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.email_verified:
        return user

    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def reset_user_password(
    session: Session,
    token: str,
    new_password: str,
) -> None:
    user_id = decode_password_reset_token(token)
    user = session.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Invalid or expired password reset link.",
        )

    user.password_hash = hash_password(new_password)

    session.add(user)
    session.commit()
