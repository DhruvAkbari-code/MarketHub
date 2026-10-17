import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

import razorpay
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.config import get_settings
from core_services.models.inventory import Inventory
from core_services.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from core_services.models.user import User
from core_services.schemas.order_schema import (
    PaymentCreateResponse,
    PaymentStatusResponse,
)

log = logging.getLogger(__name__)
settings = get_settings()
rzp = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

METHOD_MAP: dict[str, PaymentMethod] = {
    "card": PaymentMethod.CREDIT_CARD,
    "upi": PaymentMethod.UPI,
    "wallet": PaymentMethod.WALLET,
}


def to_paise(amount: Decimal) -> int:
    normalized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(normalized * 100)


def _ensure_gateway_configured() -> None:
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Online payments are not configured.",
        )


def _response(payment: Payment) -> PaymentCreateResponse:
    return PaymentCreateResponse(
        payment_id=payment.payment_id,
        order_id=payment.order_id,
        razorpay_order_id=payment.gateway_id,
        amount=to_paise(payment.amount),
        currency=payment.currency,
        key_id=settings.RAZORPAY_KEY_ID,
    )


async def create_payment(
    db: AsyncSession,
    user: User,
    order_id: UUID,
) -> PaymentCreateResponse:
    _ensure_gateway_configured()

    # Lock the order to avoid two concurrent calls creating distinct gateway orders.
    order_result = await db.exec(
        select(Order)
        .where(Order.order_id == order_id, Order.user_id == user.id)
        .with_for_update()
    )
    order = order_result.first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order is not waiting for payment.",
        )

    existing_result = await db.exec(
        select(Payment).where(Payment.order_id == order_id).with_for_update()
    )
    existing = existing_result.first()
    if existing and existing.status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order has already been paid.",
        )
    if existing and existing.status == PaymentStatus.PENDING:
        # Reuse the pending attempt; repeated client calls must not create another order.
        return _response(existing)

    amount_paise = to_paise(order.total_amount)
    if amount_paise <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The payment amount must be greater than zero.",
        )

    try:
        razorpay_order = await asyncio.to_thread(
            rzp.order.create,
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": str(order.order_id),
                "notes": {"internal_order_id": str(order.order_id)},
            },
        )
    except Exception as exc:
        log.exception("Could not create Razorpay order for internal order %s", order_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider could not create the payment order.",
        ) from exc

    if existing is None:
        payment = Payment(
            order_id=order_id,
            gateway_id=razorpay_order["id"],
            amount=order.total_amount,
            currency="INR",
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
    else:
        # Keep one payment row per order in this schema. A retry replaces the failed
        # gateway order; for a full audit trail, use a separate PaymentAttempt table.
        existing.gateway_id = razorpay_order["id"]
        existing.gateway_payment_id = None
        existing.gateway_refund_id = None
        existing.method = None
        existing.amount = order.total_amount
        existing.currency = "INR"
        existing.status = PaymentStatus.PENDING
        existing.completed_at = None
        payment = existing

    try:
        await db.commit()
        await db.refresh(payment)
    except IntegrityError as exc:
        await db.rollback()
        log.exception("Payment row conflicted while creating a Razorpay order")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A payment attempt was created concurrently. Please retry once.",
        ) from exc
    return _response(payment)


async def get_payment_for_user(
    db: AsyncSession,
    user: User,
    razorpay_order_id: str,
) -> Payment:
    result = await db.exec(
        select(Payment).where(Payment.gateway_id == razorpay_order_id)
    )
    payment = result.first()
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment order not found.",
        )
    order = await db.get(Order, payment.order_id)
    if order is None or order.user_id != user.id:
        # Do not reveal whether another customer's Razorpay order exists.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment order not found.",
        )
    return payment


async def mark_paid(
    db: AsyncSession,
    gateway_order_id: str,
    gateway_payment_id: str,
    method: str | None,
) -> None:
    """Process a captured payment idempotently and finalize reserved inventory."""
    payment_result = await db.exec(
        select(Payment).where(Payment.gateway_id == gateway_order_id).with_for_update()
    )
    payment = payment_result.first()
    if payment is None or payment.status in {
        PaymentStatus.COMPLETED,
        PaymentStatus.REFUND_PENDING,
        PaymentStatus.REFUNDED,
    }:
        return

    order_result = await db.exec(
        select(Order).where(Order.order_id == payment.order_id).with_for_update()
    )
    order = order_result.first()
    if order is None:
        log.error(
            "Payment %s references missing order %s",
            payment.payment_id,
            payment.order_id,
        )
        raise RuntimeError("Payment references a missing order.")

    now = datetime.now(timezone.utc)
    mapped_method = METHOD_MAP.get((method or "").lower())

    if order.status == OrderStatus.CANCELLED:
        # A captured payment racing with cancellation needs a Razorpay refund. This
        # is deliberately surfaced in logs rather than falsely claiming it was refunded.
        payment.status = PaymentStatus.COMPLETED
        payment.gateway_payment_id = gateway_payment_id
        payment.method = mapped_method
        payment.completed_at = now
        await db.commit()
        log.critical(
            "CAPTURED PAYMENT NEEDS REFUND: order_id=%s payment_id=%s gateway_payment_id=%s",
            order.order_id,
            payment.payment_id,
            gateway_payment_id,
        )
        return

    if order.status != OrderStatus.PENDING_PAYMENT:
        # A different successful event may have advanced the order already. Avoid
        # incrementing sold stock twice, but still record the captured transaction.
        payment.status = PaymentStatus.COMPLETED
        payment.gateway_payment_id = gateway_payment_id
        payment.method = mapped_method
        payment.completed_at = now
        await db.commit()
        log.warning(
            "Payment captured for order %s in unexpected status %s",
            order.order_id,
            order.status.value,
        )
        return

    item_result = await db.exec(
        select(OrderItem).where(OrderItem.order_id == order.order_id)
    )
    try:
        for item in item_result.all():
            inventory_result = await db.execute(
                update(Inventory)
                .where(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id == UUID(str(item.variant_id)),
                )
                .values(sold_qty=Inventory.sold_qty + item.quantity)
                .returning(Inventory.inventory_id)
            )
            if inventory_result.first() is None:
                raise RuntimeError(
                    f"Inventory row missing while finalizing paid order {order.order_id}."
                )

        payment.status = PaymentStatus.COMPLETED
        payment.gateway_payment_id = gateway_payment_id
        payment.method = mapped_method
        payment.completed_at = now
        order.status = OrderStatus.PAID
        order.paid_at = now
        order.updated_at = now
        await db.commit()
    except Exception:
        await db.rollback()
        raise


async def mark_failed(db: AsyncSession, gateway_order_id: str) -> None:
    payment_result = await db.exec(
        select(Payment).where(Payment.gateway_id == gateway_order_id).with_for_update()
    )
    payment = payment_result.first()
    if payment is not None and payment.status == PaymentStatus.PENDING:
        payment.status = PaymentStatus.FAILED
        await db.commit()


async def refund_order(db: AsyncSession, order_id: UUID) -> dict[str, str]:
    """Issue a full Razorpay refund for a completed payment. Partial refunds are not supported."""
    _ensure_gateway_configured()
    order_result = await db.exec(
        select(Order).where(Order.order_id == order_id).with_for_update()
    )
    order = order_result.first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )

    payment_result = await db.exec(
        select(Payment).where(Payment.order_id == order_id).with_for_update()
    )
    payment = payment_result.first()
    if payment is None or not payment.gateway_payment_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order has no completed online payment to refund.",
        )
    if payment.status == PaymentStatus.REFUNDED:
        return {
            "status": "refunded",
            "refund_id": payment.gateway_refund_id or "already-refunded",
        }
    if payment.status == PaymentStatus.REFUND_PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A refund attempt is already pending or needs reconciliation. "
                "Check the Razorpay dashboard before retrying to avoid a duplicate refund."
            ),
        )
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only a completed payment can be refunded.",
        )

    # Persist this state before calling the gateway. If the network result is ambiguous,
    # a second admin request will not accidentally issue a duplicate refund.
    payment.status = PaymentStatus.REFUND_PENDING
    await db.commit()

    try:
        refund = await asyncio.to_thread(
            rzp.payment.refund,
            payment.gateway_payment_id,
            {
                "amount": to_paise(payment.amount),
                "notes": {"internal_order_id": str(order.order_id)},
            },
        )
    except Exception as exc:
        log.exception(
            "Razorpay refund result is uncertain for order %s; reconcile before retrying",
            order.order_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The refund result could not be confirmed. Check Razorpay before retrying; "
                "the payment has been marked for reconciliation."
            ),
        ) from exc

    payment.gateway_refund_id = refund.get("id")
    payment.status = PaymentStatus.REFUNDED
    order.status = OrderStatus.REFUNDED
    order.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "refunded", "refund_id": payment.gateway_refund_id or "unknown"}


async def mark_refunded_by_gateway_payment_id(
    db: AsyncSession, gateway_payment_id: str, gateway_refund_id: str | None
) -> None:
    result = await db.exec(
        select(Payment)
        .where(Payment.gateway_payment_id == gateway_payment_id)
        .with_for_update()
    )
    payment = result.first()
    if payment is None or payment.status == PaymentStatus.REFUNDED:
        return
    order_result = await db.exec(
        select(Order).where(Order.order_id == payment.order_id).with_for_update()
    )
    order = order_result.first()
    payment.status = PaymentStatus.REFUNDED
    payment.gateway_refund_id = gateway_refund_id or payment.gateway_refund_id
    if order is not None:
        order.status = OrderStatus.REFUNDED
        order.updated_at = datetime.now(timezone.utc)
    await db.commit()


async def get_payment_status_for_user(
    db: AsyncSession, user: User, order_id: UUID
) -> PaymentStatusResponse:
    order = await db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    result = await db.exec(select(Payment).where(Payment.order_id == order_id))
    payment = result.first()
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payment attempt exists for this order yet.",
        )
    return PaymentStatusResponse(
        payment_id=payment.payment_id,
        order_id=payment.order_id,
        status=payment.status,
        method=payment.method,
        amount=payment.amount,
        currency=payment.currency,
        created_at=payment.created_at,
        completed_at=payment.completed_at,
    )
