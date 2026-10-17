import asyncio
import json
import logging
from uuid import UUID

import razorpay
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_current_user, get_db
from core_services.config import get_settings
from core_services.models.user import User
from core_services.schemas.order_schema import (
    PaymentCreate,
    PaymentCreateResponse,
    PaymentVerify,
    PaymentStatusResponse,
)
from core_services.services import payment_service as service

log = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(tags=["payments"])


@router.post("/payments/create", response_model=PaymentCreateResponse)
async def create_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentCreateResponse:
    return await service.create_payment(db, user, payload.order_id)


@router.get("/payments/orders/{order_id}", response_model=PaymentStatusResponse)
async def get_order_payment_status(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentStatusResponse:
    return await service.get_payment_status_for_user(db, user, order_id)


@router.post("/payments/verify")
async def verify_payment(
    payload: PaymentVerify,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Verify the checkout signature and independently validate the gateway payment."""
    payment = await service.get_payment_for_user(db, user, payload.razorpay_order_id)

    try:
        service.rzp.utility.verify_payment_signature(payload.model_dump())
    except razorpay.errors.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature.",
        ) from exc

    try:
        gateway_payment = await asyncio.to_thread(
            service.rzp.payment.fetch,
            payload.razorpay_payment_id,
        )
    except Exception as exc:
        log.exception(
            "Could not fetch Razorpay payment %s", payload.razorpay_payment_id
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not verify the payment with the payment provider.",
        ) from exc

    if gateway_payment.get("order_id") != payload.razorpay_order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The payment does not belong to this Razorpay order.",
        )
    if int(gateway_payment.get("amount", -1)) != service.to_paise(payment.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The payment amount does not match the order amount.",
        )
    if gateway_payment.get("currency") != payment.currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The payment currency does not match the order currency.",
        )

    gateway_status = gateway_payment.get("status")
    if gateway_status == "captured":
        await service.mark_paid(
            db,
            payload.razorpay_order_id,
            payload.razorpay_payment_id,
            gateway_payment.get("method"),
        )
        return {"status": "paid"}
    if gateway_status == "authorized":
        # Wait for payment.captured webhook; an authorization is not a captured payment.
        return {"status": "authorized", "message": "Waiting for payment capture."}
    if gateway_status == "failed":
        await service.mark_failed(db, payload.razorpay_order_id)
        return {"status": "failed"}

    return {"status": str(gateway_status or "processing")}


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(default=""),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Razorpay's signed webhook is the primary payment event source."""
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment webhooks are not configured.",
        )
    raw_body = await request.body()
    try:
        body = raw_body.decode("utf-8")
        service.rzp.utility.verify_webhook_signature(
            body,
            x_razorpay_signature,
            settings.RAZORPAY_WEBHOOK_SECRET,
        )
    except (UnicodeDecodeError, razorpay.errors.SignatureVerificationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature or body.",
        ) from exc

    try:
        event = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook JSON.",
        ) from exc

    event_name = event.get("event")
    entity = event.get("payload", {}).get("payment", {}).get("entity", {})

    if event_name in {"payment.captured", "payment.failed"}:
        gateway_order_id = entity.get("order_id")
        gateway_payment_id = entity.get("id")
        if not gateway_order_id or not gateway_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment event is missing its order/payment ID.",
            )
        if event_name == "payment.captured":
            await service.mark_paid(
                db,
                gateway_order_id,
                gateway_payment_id,
                entity.get("method"),
            )
        else:
            await service.mark_failed(db, gateway_order_id)
    elif event_name == "refund.processed":
        refund_entity = event.get("payload", {}).get("refund", {}).get("entity", {})
        gateway_payment_id = refund_entity.get("payment_id")
        gateway_refund_id = refund_entity.get("id")
        if gateway_payment_id:
            await service.mark_refunded_by_gateway_payment_id(
                db, gateway_payment_id, gateway_refund_id
            )

    # Acknowledge valid but unused event types so Razorpay does not retry them.
    return {"status": "ok"}
