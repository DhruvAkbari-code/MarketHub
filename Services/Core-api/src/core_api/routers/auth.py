from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status, Body
from sqlmodel import Session
import uuid

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
    VendorRegisterRequest,
    UpdateProfileRequest,
    ChangePasswordRequest,
    AddressRequest,
    AddressResponse,
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


@router.post(
    "/register/vendor",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_vendor(
    payload: VendorRegisterRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = auth_service.register_vendor(session, payload)
    token = create_verification_token(user.id)
    background_tasks.add_task(send_verification_email, user.email, user.username, token)
    return RegisterResponse(id=user.id, email=user.email, username=user.username)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return auth_service.update_profile(session, current_user.id, payload)


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    auth_service.change_password(session, current_user.id, payload)
    return {"message": "Password updated successfully."}


@router.get("/addresses", response_model=list[AddressResponse])
def get_addresses(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return auth_service.list_addresses(session, current_user.id)


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_address(
    payload: AddressRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return auth_service.create_address(session, current_user.id, payload)


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def edit_address(
    address_id: uuid.UUID,
    payload: AddressRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return auth_service.update_address(session, current_user.id, address_id, payload)


@router.post("/addresses/{address_id}/default", response_model=AddressResponse)
def make_default_address(
    address_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return auth_service.set_default_address(session, current_user.id, address_id)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_address(
    address_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    auth_service.delete_address(session, current_user.id, address_id)
