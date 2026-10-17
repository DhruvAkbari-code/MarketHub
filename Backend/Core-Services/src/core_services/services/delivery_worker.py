import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import update

from core_services.dependencies import get_db
from core_services.models.order import Order, OrderStatus

log = logging.getLogger(__name__)

DELIVERY_AFTER = timedelta(minutes=10)  # set to 1 minute while testing
CHECK_EVERY_SECONDS = 30

# Every paid-but-not-finished stage. CANCELLED, REFUNDED and DELIVERED are left alone.
IN_PROGRESS = [
    OrderStatus.PAID,
    OrderStatus.CONFIRMED,
    OrderStatus.PROCESSING,
    OrderStatus.SHIPPED,
    OrderStatus.OUT_FOR_DELIVERY,
]


async def deliver_due_orders() -> int:
    """Marks orders paid more than 10 minutes ago as DELIVERED. Returns how many."""
    now = datetime.now(timezone.utc)
    async for db in get_db():
        result = await db.execute(
            update(Order)
            .where(
                Order.status.in_(IN_PROGRESS),
                Order.paid_at.is_not(None),
                Order.paid_at <= now - DELIVERY_AFTER,
            )
            .values(status=OrderStatus.DELIVERED, updated_at=now)
        )
        await db.commit()
        return result.rowcount or 0
    return 0


async def auto_deliver_loop() -> None:
    """Demo only: no real shipping happens, the status just moves on a timer."""
    while True:
        try:
            count = await deliver_due_orders()
            if count:
                log.info("Auto-delivered %s order(s)", count)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Auto delivery run failed")
        await asyncio.sleep(CHECK_EVERY_SECONDS)
