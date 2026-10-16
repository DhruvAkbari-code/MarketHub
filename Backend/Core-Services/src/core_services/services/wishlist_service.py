from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.models.wishlist import Wishlist


async def add(
    db: AsyncSession, user_id: UUID, product_id: str, variant_id: UUID
) -> Wishlist:
    row = Wishlist(user_id=user_id, product_id=product_id, variant_id=variant_id)
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Already in your wishlist.")
    await db.refresh(row)
    return row


async def list_for_user(db: AsyncSession, user_id: UUID):
    result = await db.exec(
        select(Wishlist)
        .where(Wishlist.user_id == user_id)
        .order_by(Wishlist.added_at.desc())
    )
    return result.all()


async def remove(db: AsyncSession, user_id: UUID, wishlist_id: UUID) -> None:
    row = await db.get(Wishlist, wishlist_id)
    if not row or row.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not in your wishlist.")
    await db.delete(row)
    await db.commit()
