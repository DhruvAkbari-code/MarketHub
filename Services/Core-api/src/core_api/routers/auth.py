from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlmodel import Session

from core_api.database import get_session
from core_api.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    VerifyEmailRequest,
)
from core_api.security import create_verification_token
from core_api.services import auth_service
from core_api.services.email import send_verification_email

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
