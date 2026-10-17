import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.models.inventory import Inventory
from core_services.models.order import (
    Coupon,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
)
from core_services.models.user import User
from core_services.schemas.order_schema import (
    CheckoutRequest,
    OrderItemResponse,
    OrderResponse,
    VendorOrderStatusUpdate,
)
from core_services.services import cart_service, checkout_service

log = logging.getLogger(__name__)


def _variant_uuid(variant_id: str | None) -> UUID:
    if not variant_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A cart item has no valid variant ID.",
        )
    try:
        return UUID(str(variant_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A cart item has an invalid variant ID.",
        )


async def _responses(db: AsyncSession, orders: list[Order]) -> list[OrderResponse]:
    if not orders:
        return []

    order_ids = [order.order_id for order in orders]
    result = await db.exec(select(OrderItem).where(OrderItem.order_id.in_(order_ids)))
    items_by_order: dict[UUID, list[OrderItemResponse]] = {}
    for item in result.all():
        items_by_order.setdefault(item.order_id, []).append(
            OrderItemResponse.model_validate(item.model_dump())
        )

    return [
        OrderResponse(
            **order.model_dump(),
            items=items_by_order.get(order.order_id, []),
        )
        for order in orders
    ]


async def create_orders(
    db: AsyncSession,
    user: User,
    data: CheckoutRequest,
) -> list[OrderResponse]:
    groups, coupon = await checkout_service.build_checkout(db, user, data)
    orders: list[Order] = []

    try:
        for group in groups:
            order = Order(
                user_id=user.id,
                vendor_id=group.vendor_id,
                address_id=data.address_id,
                coupon_id=coupon.coupon_id if coupon else None,
                subtotal=group.subtotal,
                tax_amount=group.tax_amount,
                shipping_cost=group.shipping_cost,
                discount_amount=group.discount_amount,
                total_amount=group.total_amount,
                shipping_method=data.shipping_method,
            )
            db.add(order)
            # Ensure the parent row exists before inserting its items. The transaction
            # is still uncommitted, so all order/stock writes remain atomic.
            await db.flush()

            for item in group.items:
                result = await db.execute(
                    update(Inventory)
                    .where(
                        Inventory.product_id == item.product_id,
                        Inventory.variant_id == _variant_uuid(item.variant_id),
                        Inventory.available_qty >= item.quantity,
                    )
                    .values(available_qty=Inventory.available_qty - item.quantity)
                    .returning(Inventory.inventory_id)
                )
                if result.first() is None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Not enough stock for {item.product_name}.",
                    )

                db.add(
                    OrderItem(
                        order_id=order.order_id,
                        product_id=item.product_id,
                        variant_id=item.variant_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        total_price=item.total_price,
                    )
                )
            orders.append(order)

        await db.commit()
    except Exception:
        await db.rollback()
        raise

    for order in orders:
        await db.refresh(order)

    # The orders are already committed. A Redis/cart cleanup failure must not make
    # the API return an error that could cause the client to submit checkout again.
    try:
        await cart_service.clear(user.id)
    except Exception:
        log.exception(
            "Orders were created but cart cleanup failed for user %s", user.id
        )
    return await _responses(db, orders)


async def list_orders(
    db: AsyncSession,
    user: User,
    skip: int,
    limit: int,
) -> list[OrderResponse]:
    result = await db.exec(
        select(Order)
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return await _responses(db, list(result.all()))


async def get_order(db: AsyncSession, user: User, order_id: UUID) -> OrderResponse:
    result = await db.exec(
        select(Order).where(Order.order_id == order_id, Order.user_id == user.id)
    )
    order = result.first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    return (await _responses(db, [order]))[0]


async def cancel_order(db: AsyncSession, user: User, order_id: UUID) -> OrderResponse:
    result = await db.exec(
        select(Order)
        .where(Order.order_id == order_id, Order.user_id == user.id)
        .with_for_update()
    )
    order = result.first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only orders awaiting payment can be cancelled.",
        )

    payment_result = await db.exec(
        select(Payment).where(Payment.order_id == order_id).with_for_update()
    )
    payment = payment_result.first()
    if payment is not None and payment.status == PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A payment attempt is still pending. Wait for Razorpay to report its "
                "result before cancelling this order."
            ),
        )

    item_result = await db.exec(select(OrderItem).where(OrderItem.order_id == order_id))
    try:
        for item in item_result.all():
            inventory_result = await db.execute(
                update(Inventory)
                .where(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id == _variant_uuid(item.variant_id),
                )
                .values(available_qty=Inventory.available_qty + item.quantity)
                .returning(Inventory.inventory_id)
            )
            if inventory_result.first() is None:
                raise RuntimeError(
                    f"Inventory row missing while releasing stock for order {order_id}."
                )

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(order)
    return (await _responses(db, [order]))[0]


_VENDOR_TRANSITIONS: dict[OrderStatus, OrderStatus] = {
    OrderStatus.PAID: OrderStatus.CONFIRMED,
    OrderStatus.CONFIRMED: OrderStatus.PROCESSING,
    OrderStatus.PROCESSING: OrderStatus.SHIPPED,
    OrderStatus.SHIPPED: OrderStatus.OUT_FOR_DELIVERY,
    OrderStatus.OUT_FOR_DELIVERY: OrderStatus.DELIVERED,
}


async def list_vendor_orders(
    db: AsyncSession,
    vendor: User,
    skip: int,
    limit: int,
) -> list[OrderResponse]:
    result = await db.exec(
        select(Order)
        .where(Order.vendor_id == vendor.id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return await _responses(db, list(result.all()))


async def update_vendor_order_status(
    db: AsyncSession,
    vendor: User,
    order_id: UUID,
    payload: VendorOrderStatusUpdate,
) -> OrderResponse:
    result = await db.exec(
        select(Order)
        .where(Order.order_id == order_id, Order.vendor_id == vendor.id)
        .with_for_update()
    )
    order = result.first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )

    expected_next_status = _VENDOR_TRANSITIONS.get(order.status)
    if expected_next_status is None or payload.status != expected_next_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid status transition from {order.status.value}. "
                f"Expected {expected_next_status.value if expected_next_status else 'no vendor transition'}."
            ),
        )

    if payload.status in {OrderStatus.SHIPPED, OrderStatus.OUT_FOR_DELIVERY}:
        tracking_number = payload.tracking_number or order.tracking_number
        if not tracking_number:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A tracking number is required for shipped orders.",
            )
        order.tracking_number = tracking_number
    elif payload.tracking_number:
        order.tracking_number = payload.tracking_number

    order.status = payload.status
    order.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(order)
    return (await _responses(db, [order]))[0]


async def list_all_orders(
    db: AsyncSession, skip: int, limit: int
) -> list[OrderResponse]:
    result = await db.exec(
        select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    )
    return await _responses(db, list(result.all()))
