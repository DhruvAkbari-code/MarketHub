from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_db, require_roles
from core_services.models.user import Role, User
from core_services.schemas.order_schema import OrderResponse
from core_services.services.order_service import list_all_orders
from core_services.services import payment_service

router = APIRouter(prefix="/admin/orders", tags=["admin orders"])


@router.get("", response_model=list[OrderResponse])
async def admin_list_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_roles(Role.admin)),
) -> list[OrderResponse]:
    return await list_all_orders(db, skip, limit)


@router.post("/{order_id}/refund")
async def admin_refund_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_roles(Role.admin)),
) -> dict[str, str]:
    """Issue a full payment refund. Partial refunds are not implemented."""
    return await payment_service.refund_order(db, order_id)
