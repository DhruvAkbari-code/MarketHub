from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from core_services.models.order import (
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    ShippingMethod,
)


class CheckoutRequest(BaseModel):
    address_id: UUID
    shipping_method: ShippingMethod = ShippingMethod.STANDARD
    coupon_code: str | None = Field(default=None, min_length=3, max_length=30)


class CheckoutItem(BaseModel):
    product_id: str
    variant_id: str
    product_name: str
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    total_price: Decimal = Field(ge=0)


class CheckoutGroup(BaseModel):
    """A single vendor's group; creating a checkout makes one Order per group."""

    vendor_id: UUID
    items: list[CheckoutItem]
    subtotal: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal
    total_amount: Decimal


class CheckoutSummary(BaseModel):
    orders: list[CheckoutGroup]
    grand_total: Decimal


class OrderItemResponse(BaseModel):
    order_item_id: UUID
    product_id: str
    variant_id: str | None
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: UUID
    user_id: UUID
    vendor_id: UUID
    address_id: UUID
    coupon_id: UUID | None
    subtotal: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    status: OrderStatus
    shipping_method: ShippingMethod
    tracking_number: str | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class CouponCreate(BaseModel):
    code: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    discount_percent: int = Field(ge=1, le=100)


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    coupon_id: UUID
    code: str
    discount_percent: int
    is_active: bool
    created_at: datetime


class PaymentCreate(BaseModel):
    order_id: UUID


class PaymentCreateResponse(BaseModel):
    payment_id: UUID
    order_id: UUID
    razorpay_order_id: str
    amount: int  # Paise, as Razorpay Checkout expects.
    currency: str
    key_id: str


class PaymentVerify(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=255)
    razorpay_payment_id: str = Field(min_length=1, max_length=255)
    razorpay_signature: str = Field(min_length=1, max_length=512)


class VendorOrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: str | None = Field(default=None, max_length=100)


class PaymentStatusResponse(BaseModel):
    payment_id: UUID
    order_id: UUID
    status: PaymentStatus
    method: PaymentMethod | None
    amount: Decimal
    currency: str
    created_at: datetime
    completed_at: datetime | None
