from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from sqlmodel import Session

from fastapi.responses import JSONResponse


from core_api.dependencies import get_current_user
from core_api.models.user import User

from core_api.database import get_session
from core_api.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    VerifyEmailRequest,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
    LoginRequest,
    LoginResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from core_api.security import (
    create_verification_token,
    create_password_reset_token,
    create_access_token,
)
from core_api.services import auth_service
from core_api.services.email import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = auth_service.register_user(session, payload)
    token = create_verification_token(user.id)
    background_tasks.add_task(send_verification_email, user.email, user.username, token)
    return RegisterResponse(id=user.id, email=user.email, username=user.username)


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    payload: VerifyEmailRequest,
    session: Session = Depends(get_session),
):
    user = auth_service.verify_email(session, payload.token)
    return {"message": "Email verified successfully", "email": user.email}


@router.post("/google", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def google_auth(payload: GoogleAuthRequest, session: Session = Depends(get_session)):
    access_token, is_new = auth_service.google_login(session, payload.id_token)
    return TokenResponse(access_token=access_token, is_new_user=is_new)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = auth_service.login_user(session, str(payload.email), payload.password)
    if not user.email_verified:
        token = create_verification_token(user.id)

        background_tasks.add_task(
            send_verification_email, user.email, user.username, token
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": (
                    "Your email is not verified. A new verification link "
                    "has been sent to your email. Please verify your email "
                    "before logging in."
                )
            },
            background=background_tasks,
        )

    return LoginResponse(
        access_token=create_access_token(user.id),
        role=user.role,
    )


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    email = str(payload.email).strip().lower()
    user = auth_service.get_user_by_email(session, email)

    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "This email is not registered.",
        )

    if not user.is_active:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "This account is disabled.",
        )

    if not user.password_hash:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "This account uses Google sign-in. Please log in with Google.",
        )

    token = create_password_reset_token(user.id)

    background_tasks.add_task(
        send_password_reset_email,
        user.email,
        user.username,
        token,
    )

    return {"message": "A password reset link has been sent to your email."}


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    session: Session = Depends(get_session),
):
    auth_service.reset_user_password(
        session,
        payload.token,
        payload.new_password,
    )

    return {
        "message": (
            "Password reset successfully. Please log in " "with your new password."
        )
    }
