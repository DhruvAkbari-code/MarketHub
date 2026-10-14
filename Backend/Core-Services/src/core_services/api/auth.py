import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.core.security import (
    create_verification_token,
    create_access_token,
    create_password_reset_token,
)
from core_services.dependencies import get_db_session
from core_services.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    VerifyEmailRequest,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RegisterVendor,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from core_services.services.auth_service import (
    register_user,
    verify_email,
    google_login,
    login_user,
    register_vendor,
    get_user_by_email,
    reset_user_password,
)
from core_services.services.email import (
    send_verification_email,
    send_password_reset_email,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> RegisterResponse:
    user = await register_user(session, payload)
    token = create_verification_token(user.id)
    background_tasks.add_task(send_verification_email, user.email, user.username, token)
    print(token)
    return RegisterResponse(id=user.id, email=user.email, username=user.username)


@router.post(
    "/register/vendor",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registerVendor(
    payload: RegisterVendor,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    user = await register_vendor(session, payload)
    token = create_verification_token(user.id)
    background_tasks.add_task(send_verification_email, user.email, user.username, token)
    return RegisterResponse(id=user.id, email=user.email, username=user.username)


@router.get("/dev/verification-token/{user_id}", include_in_schema=False)
async def dev_get_verification_token(user_id: uuid.UUID):
    if os.getenv("ENVIRONMENT", "development") != "development":
        raise HTTPException(status_code=404, detail="Not found")
    return {"token": create_verification_token(user_id)}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email_endpoint(
    payload: VerifyEmailRequest, session: AsyncSession = Depends(get_db_session)
):
    user = await verify_email(session, payload.token)
    return {
        "message": "Email verified successfully.",
        "email": user.email,
    }


@router.post("/google", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def google_auth(
    payload: GoogleAuthRequest,
    session: AsyncSession = Depends(get_db_session),
):
    access_token, is_new = await google_login(session, payload.id_token)
    return TokenResponse(access_token=access_token, is_new_user=is_new)


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    user = await login_user(session, str(payload.email), payload.password)

    if not user.email_verified:
        token = create_verification_token(user.id)
        background_tasks.add_task(
            send_verification_email, user.email, user.username, token
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your email is not verified. A new verification link has been "
                "sent to your email. Please verify your email before logging in."
            ),
        )

    return LoginResponse(
        access_token=create_access_token(user.id),
        role=user.role,
    )


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    email = str(payload.email).strip().lower()
    user = await get_user_by_email(session, email)

    if user and user.is_active and user.password_hash:
        token = create_password_reset_token(user.id)
        background_tasks.add_task(
            send_password_reset_email, user.email, user.username, token
        )

    return {
        "message": "If that email is registered, a password reset link has been sent.",
        "token": token,
    }


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest, session: AsyncSession = Depends(get_db_session)
):
    await reset_user_password(session, payload.token, payload.new_password)

    return {
        "message": ("Password reset successfully. Please log in with your new password")
    }
