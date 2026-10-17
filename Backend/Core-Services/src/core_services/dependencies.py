from uuid import UUID
from collections.abc import AsyncIterator
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from core_services.database import get_session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core_services.models.user import User, Role
from core_services.core.security import decode_access_token

bearer_schema = HTTPBearer()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with get_session() as session:
        yield session


get_db = get_db_session
SessioDep = Annotated[AsyncSession, Depends(get_db_session)]


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_schema),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        decoded_user_id = decode_access_token(credentials.credentials)
        user_id = UUID(str(decoded_user_id))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


get_current_user = current_user


def require_roles(*allowed_roles: Role):
    async def role_checker(current_user: User = Depends(current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return role_checker
