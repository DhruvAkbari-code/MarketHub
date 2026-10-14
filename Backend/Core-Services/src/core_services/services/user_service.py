from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import FastAPI, HTTPException, status
from sqlmodel import select

from core_services.schemas.user_schema import (
    UpdateProfileRequest,
    ChangePasswordRequest,
    AddressRequest,
    AddressResponse,
)
from core_services.models.user import User
from core_services.models.address import Address
from core_services.core.security import verify_password, hash_password

MAX_ADDRESSES = 4


async def update_profile(
    session: AsyncSession, user_id, data: UpdateProfileRequest
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    changes = data.model_dump(exclude_unset=True)

    if "username" in changes and changes["username"] is not None:
        user.username = data.username

    if "phone" in changes and changes["phone"] is not None:
        user.phone = data.phone

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def change_password(
    session: AsyncSession, user_id, data: ChangePasswordRequest
) -> None:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if not user.password_hash:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "This account uses Google Sign-in and has no password to change.",
        )
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Current password is incorrect."
        )
    if verify_password(data.new_password, user.password_hash):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "New password must be different from the current one.",
        )

    user.password_hash = hash_password(data.new_password)
    session.add(user)
    await session.commit()


async def list_addresses(session: AsyncSession, user_id) -> list[Address]:
    result = await session.exec(
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(Address.is_default.desc(), Address.created_at)
    )
    return list(result.all())


async def _clear_default(session: AsyncSession, user_id) -> None:
    for a in await list_addresses(session, user_id):
        if a.is_default:
            a.is_default = False
            session.add(a)


async def create_address(
    session: AsyncSession, user_id, data: AddressRequest
) -> Address:
    existing = await list_addresses(session, user_id)
    if len(existing) >= MAX_ADDRESSES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"You can save up to {MAX_ADDRESSES} addresses.",
        )
    make_deafult = data.is_default or len(existing) == 0
    if make_deafult:
        await _clear_default(session, user_id)
    address = Address(
        user_id=user_id,
        **data.model_dump(exclude={"is_default"}),
        is_default=make_deafult,
    )
    session.add(address)
    await session.commit()
    await session.refresh(address)
    return address


async def _get_own_address(session: AsyncSession, user_id, address_id) -> Address:
    address = await session.get(Address, address_id)
    if address is None or address.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Address not found")
    return address


async def update_address(
    session: AsyncSession, user_id, address_id, data: AddressRequest
) -> Address:
    address = await _get_own_address(session, user_id, address_id)

    if data.is_default and not address.is_default:
        await _clear_default(session, user_id)

    for field, value in data.model_dump(exclude={"is_default"}).items():
        setattr(address, field, value)

    address.is_default = data.is_default or address.is_default
    session.add(address)
    await session.commit()
    await session.refresh(address)

    return address


async def set_default_address(session: AsyncSession, user_id, address_id) -> Address:
    address = await _get_own_address(session, user_id, address_id)
    await _clear_default(session, user_id)
    address.is_default = True
    session.add(address)
    await session.commit()
    await session.refresh(address)

    return address


async def delete_address(session: AsyncSession, user_id, address_id) -> None:
    address = await _get_own_address(session, user_id, address_id)
    was_default = address.is_default
    await session.delete(address)
    await session.commit()

    if was_default:
        remaining = await list_addresses(session, user_id)
        if remaining:
            remaining[0].is_default = True
            session.add(remaining[0])
            await session.commit()
