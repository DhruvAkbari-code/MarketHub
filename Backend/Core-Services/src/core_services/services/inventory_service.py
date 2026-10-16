from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.models.inventory import Inventory


async def create(
    db: AsyncSession, product_id: str, variant_id: UUID, vendor_id: UUID, quantity: int
) -> Inventory:
    existing = await db.exec(
        select(Inventory).where(
            Inventory.product_id == product_id, Inventory.variant_id == variant_id
        )
    )
    if existing.first():
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Stock already exists for this variant."
        )

    row = Inventory(
        product_id=product_id,
        variant_id=variant_id,
        vendor_id=vendor_id,
        available_qty=quantity,
        last_restocked_at=datetime.now(timezone.utc) if quantity > 0 else None,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def list_by(db: AsyncSession, *conditions):
    result = await db.exec(select(Inventory).where(*conditions))
    return result.all()


async def restock(db: AsyncSession, inventory_id: UUID, qty: int) -> Inventory:
    """Adds to available stock in one atomic UPDATE."""
    result = await db.execute(
        update(Inventory)
        .where(Inventory.inventory_id == inventory_id)
        .values(
            available_qty=Inventory.available_qty + qty,
            last_restocked_at=datetime.now(timezone.utc),
        )
        .returning(Inventory.inventory_id)
    )
    if result.first() is None:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Stock record not found.")
    await db.commit()
    return await db.get(Inventory, inventory_id, populate_existing=True)


async def sell(db: AsyncSession, product_id: str, variant_id: UUID, qty: int) -> None:
    """For checkout later: available -> sold. One atomic UPDATE, so two buyers
    can't take the last item."""
    result = await db.execute(
        update(Inventory)
        .where(
            Inventory.product_id == product_id,
            Inventory.variant_id == variant_id,
            Inventory.available_qty >= qty,
        )
        .values(
            available_qty=Inventory.available_qty - qty,
            sold_qty=Inventory.sold_qty + qty,
        )
        .returning(Inventory.inventory_id)
    )
    if result.first() is None:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Not enough stock.")
    await db.commit()
