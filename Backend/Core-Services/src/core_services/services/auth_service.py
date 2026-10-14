import asyncio
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.core.security import (
    create_access_token,
    decode_verification_token,
    hash_password,
    verify_password,
    decode_password_reset_token,
)
from core_services.models.user import Role, User
from core_services.models.vendor import VendorProfile
from core_services.schemas.auth_schema import RegisterRequest, RegisterVendor
from core_services.services.google_service import verify_google_id_token


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.exec(select(User).where(User.email == email))
    return result.first()


async def register_user(session: AsyncSession, data: RegisterRequest) -> User:
    email = str(data.email).strip().lower()
    existing_user = await get_user_by_email(session, email)
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
        email=email,
        username=data.username,
        phone=data.phone,
        role=Role.customer,
        password_hash=hash_password(data.password),
        email_verified=False,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def register_vendor(session: AsyncSession, data: RegisterVendor) -> User:
    email = str(data.email).strip().lower()
    existing_user = await get_user_by_email(session, email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email already exists. " "Please sign in instead."
            ),
        )
    user = User(
        email=email,
        username=data.username,
        phone=data.phone,
        role=Role.vendor,
        password_hash=hash_password(data.password),
        email_verified=False,
    )

    session.add(user)
    await session.flush()

    vendorProfile = VendorProfile(
        user_id=user.id,
        store_name=data.store_name,
        category=data.category,
        website=data.website,
        about=data.about,
    )
    session.add(vendorProfile)

    await session.commit()
    await session.refresh(user)
    return user


async def verify_email(session: AsyncSession, token: str) -> User:
    user_id = decode_verification_token(token)
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    if not user.email_verified:
        user.email_verified = True
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def google_login(session: AsyncSession, raw_id_token: str) -> tuple[str, bool]:
    info = await asyncio.to_thread(verify_google_id_token, raw_id_token)

    if not info.get("email_verified"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Google account email is not verified"
        )

    email = info["email"].lower()
    google_sub = info["sub"]
    picture = info.get("picture")
    display_name = info.get("name") or email.split("@")[0]

    user = await get_user_by_email(session, email)
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
    await session.commit()
    await session.refresh(user)

    return create_access_token(user.id), is_new


async def login_user(session: AsyncSession, email: str, password: str) -> User:
    email = email.strip().lower()
    user = await get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your Account is Disabled. Please contact support.",
        )

    if not user.password_hash:
        if user.google_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses Google Sign-in. Please sign in with Google.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.email_verified:
        return user

    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def reset_user_password(
    session: AsyncSession, token: str, new_password: str
) -> None:
    user_id = decode_password_reset_token(token)
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Invalid or expired password reset link"
        )
    user.password_hash = hash_password(new_password)
    session.add(user)
    await session.commit()
