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


SessioDep = Annotated[AsyncSession, Depends(get_db_session)]


async def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_schema),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    user = await session.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or disabled")
    return user


def require_roles(*allowed_roles: Role):
    async def role_checker(current_user: User = Depends(current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return role_checker
