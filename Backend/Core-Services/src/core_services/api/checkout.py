from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_current_user, get_db
from core_services.models.user import User
from core_services.schemas.order_schema import CheckoutRequest, CheckoutSummary
from core_services.services import checkout_service

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/summary", response_model=CheckoutSummary)
async def checkout_summary(
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CheckoutSummary:
    """Preview checkout. This does not create orders or reserve inventory."""
    groups, _coupon = await checkout_service.build_checkout(db, user, payload)
    grand_total = sum((group.total_amount for group in groups), Decimal("0.00"))
    return CheckoutSummary(orders=groups, grand_total=grand_total)
