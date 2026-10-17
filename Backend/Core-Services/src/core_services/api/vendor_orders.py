from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_db, require_roles
from core_services.models.user import Role, User
from core_services.schemas.order_schema import OrderResponse, VendorOrderStatusUpdate
from core_services.services import order_service

router = APIRouter(prefix="/vendor/orders", tags=["vendor orders"])


@router.get("", response_model=list[OrderResponse])
async def vendor_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    vendor: User = Depends(require_roles(Role.vendor)),
) -> list[OrderResponse]:
    return await order_service.list_vendor_orders(db, vendor, skip, limit)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def advance_order_status(
    order_id: UUID,
    payload: VendorOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    vendor: User = Depends(require_roles(Role.vendor)),
) -> OrderResponse:
    return await order_service.update_vendor_order_status(db, vendor, order_id, payload)
