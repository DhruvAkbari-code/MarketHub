import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.schemas.user_schema import (
    UserResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
    AddressRequest,
    AddressResponse,
)
from core_services.dependencies import current_user, get_db_session
from core_services.services import user_service
from core_services.models.user import User

router = APIRouter(prefix="/user", tags=["User Activities"])


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UpdateProfileRequest,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await user_service.update_profile(session, current_user.id, payload)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    await user_service.change_password(session, user.id, payload)
    return {"message": "Password updated successfully."}


@router.post(
    "/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED
)
async def add_address(
    payload: AddressRequest,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await user_service.create_address(session, current_user.id, payload)


@router.get("/addresses", response_model=list[AddressResponse])
async def get_addresses(
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await user_service.list_addresses(session, current_user.id)


@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def edit_address(
    address_id: uuid.UUID,
    payload: AddressRequest,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await user_service.update_address(
        session, current_user.id, address_id, payload
    )


@router.post("/addesses/{address_id}/default", response_model=AddressResponse)
async def make_default_address(
    address_id: uuid.UUID,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await user_service.set_default_address(session, current_user.id, address_id)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_address(
    address_id: uuid.UUID,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
):
    await user_service.delete_address(session, current_user.id, address_id)
