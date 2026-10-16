from uuid import UUID

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_db_session, require_roles
from core_services.models.inventory import Inventory
from core_services.models.product import Product
from core_services.models.user import Role, User
from core_services.schemas.inventory_schema import InventoryCreate, StockAdd
from core_services.services import inventory_service as svc

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", response_model=Inventory, status_code=status.HTTP_201_CREATED)
async def create_stock(
    payload: InventoryCreate,
    db: AsyncSession = Depends(get_db_session),
    vendor: User = Depends(require_roles(Role.vendor)),
):
    product = await Product.get(payload.product_id)
    if not product or product.vendor_id != vendor.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The product not found.")
    if not any(v.id == payload.variant_id for v in product.variants):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The variant not found.")

    return await svc.create(
        db, str(product.id), payload.variant_id, vendor.id, payload.quantity
    )


@router.get("/me", response_model=list[Inventory])
async def my_stock(
    db: AsyncSession = Depends(get_db_session),
    vendor: User = Depends(require_roles(Role.vendor)),
):
    return await svc.list_by(db, Inventory.vendor_id == vendor.id)


@router.get("/product/{product_id}", response_model=list[Inventory])
async def product_stock(
    product_id: PydanticObjectId, db: AsyncSession = Depends(get_db_session)
):
    return await svc.list_by(db, Inventory.product_id == str(product_id))


@router.patch("/{inventory_id}/restock", response_model=Inventory)
async def restock(
    inventory_id: UUID,
    payload: StockAdd,
    db: AsyncSession = Depends(get_db_session),
    vendor: User = Depends(require_roles(Role.vendor)),
):
    row = await db.get(Inventory, inventory_id)
    if not row or row.vendor_id != vendor.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Stock record not found.")
    return await svc.restock(db, inventory_id, payload.quantity)
