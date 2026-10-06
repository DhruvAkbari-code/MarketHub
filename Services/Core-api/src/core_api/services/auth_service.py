from fastapi import HTTPException, status
from sqlmodel import Session, select

from core_api.models.user import User
from core_api.schemas.auth import RegisterRequest
from core_api.security import decode_verification_token, hash_password


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def register_user(session: Session, data: RegisterRequest) -> User:
    if get_user_by_email(session, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        email=data.email,
        username=data.username,
        phone=data.phone,
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
