import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class ShippingMethod(str, enum.Enum):
    STANDARD = "STANDARD"
    EXPRESS = "EXPRESS"
    OVERNIGHT = "OVERNIGHT"
    PICKUP = "PICKUP"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    UPI = "UPI"
    WALLET = "WALLET"
    COD = "COD"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"


class Coupon(SQLModel, table=True):
    __tablename__ = "coupons"

    coupon_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    code: str = Field(max_length=30, unique=True, index=True)
    discount_percent: int = Field(ge=1, le=100)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True)
    )


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    order_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    vendor_id: uuid.UUID = Field(index=True)  # Vendor's user ID.
    address_id: uuid.UUID = Field(foreign_key="addresses.id")
    coupon_id: uuid.UUID | None = Field(default=None, foreign_key="coupons.coupon_id")

    subtotal: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    tax_amount: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    shipping_cost: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    discount_amount: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    total_amount: Decimal = Field(max_digits=12, decimal_places=2, ge=0)

    status: OrderStatus = Field(default=OrderStatus.PENDING_PAYMENT, index=True)
    shipping_method: ShippingMethod
    tracking_number: str | None = Field(default=None, max_length=100, unique=True)
    paid_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    created_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), index=True
    )
    updated_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True)
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    order_item_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="orders.order_id", index=True)
    product_id: str = Field(
        max_length=24, index=True
    )  # MongoDB ObjectId stored as hex.
    variant_id: str | None = Field(default=None, max_length=64)
    product_name: str = Field(max_length=200)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    total_price: Decimal = Field(max_digits=12, decimal_places=2, ge=0)


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    payment_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="orders.order_id", unique=True, index=True)
    gateway_id: str = Field(
        max_length=255, unique=True, index=True
    )  # Razorpay order ID.
    gateway_payment_id: str | None = Field(default=None, max_length=255, index=True)
    gateway_refund_id: str | None = Field(default=None, max_length=255, index=True)
    method: PaymentMethod | None = Field(default=None)
    amount: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    currency: str = Field(default="INR", max_length=3)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    created_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True)
    )
    completed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
