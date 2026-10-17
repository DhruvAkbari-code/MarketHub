from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_current_user, get_db
from core_services.models.user import User
from core_services.schemas.order_schema import CheckoutRequest, OrderResponse
from core_services.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "", response_model=list[OrderResponse], status_code=status.HTTP_201_CREATED
)
async def place_order(
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    """Create one order per vendor and reserve the inventory atomically."""
    return await order_service.create_orders(db, user, payload)


@router.get("", response_model=list[OrderResponse])
async def my_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    return await order_service.list_orders(db, user, skip, limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrderResponse:
    return await order_service.get_order(db, user, order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_my_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrderResponse:
    return await order_service.cancel_order(db, user, order_id)
