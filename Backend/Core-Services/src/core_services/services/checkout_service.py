from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from beanie import PydanticObjectId
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.models.address import Address
from core_services.models.order import Coupon, ShippingMethod
from core_services.models.product import Product
from core_services.models.user import User
from core_services.schemas.order_schema import (
    CheckoutGroup,
    CheckoutItem,
    CheckoutRequest,
)
from core_services.services import cart_service

TAX_RATE = Decimal(
    "0.18"
)  # Demo default only; use category-specific tax rules in production.
SHIPPING_FEE: dict[ShippingMethod, Decimal] = {
    ShippingMethod.STANDARD: Decimal("49.00"),
    ShippingMethod.EXPRESS: Decimal("99.00"),
    ShippingMethod.OVERNIGHT: Decimal("199.00"),
    ShippingMethod.PICKUP: Decimal("0.00"),
}
CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def as_decimal(value: object) -> Decimal:
    """Handle Decimal, string/numeric values, and BSON Decimal128 values."""
    to_decimal = getattr(value, "to_decimal", None)
    if callable(to_decimal):
        return to_decimal()
    return Decimal(str(value))


async def build_checkout(
    db: AsyncSession,
    user: User,
    data: CheckoutRequest,
) -> tuple[list[CheckoutGroup], Coupon | None]:
    """Revalidate address, coupon, products, variants, stock, and all totals."""
    address = await db.get(Address, data.address_id)
    if address is None or address.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The address was not found.",
        )

    coupon: Coupon | None = None
    if data.coupon_code:
        code = data.coupon_code.strip().upper()
        result = await db.exec(
            select(Coupon).where(Coupon.code == code, Coupon.is_active.is_(True))
        )
        coupon = result.first()
        if coupon is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive coupon.",
            )

    cart = await cart_service.load(user.id)
    cart_items = cart.get("items", [])
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty.",
        )

    try:
        product_ids = {PydanticObjectId(item["product_id"]) for item in cart_items}
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The cart contains an invalid product. Clear the cart and try again.",
        )

    products = await Product.find(
        {"_id": {"$in": list(product_ids)}, "is_active": True}
    ).to_list()
    products_by_id = {product.id: product for product in products}
    items_by_vendor: dict[UUID, list[CheckoutItem]] = defaultdict(list)

    for cart_item in cart_items:
        product_id = PydanticObjectId(cart_item["product_id"])
        product = products_by_id.get(product_id)
        requested_variant_id = str(cart_item.get("variant_id", ""))

        variant = None
        if product is not None:
            variant = next(
                (
                    candidate
                    for candidate in product.variants
                    if str(candidate.id) == requested_variant_id and candidate.is_active
                ),
                None,
            )

        if product is None or variant is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An item in your cart is no longer available. "
                    "Remove it and try again."
                ),
            )

        try:
            quantity = int(cart_item["quantity"])
        except (KeyError, TypeError, ValueError):
            quantity = 0
        if quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid quantity for {product.name}.",
            )

        stock = await cart_service.available_stock(db, str(product.id), variant.id)
        if stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Not enough stock for {product.name}.",
            )

        unit_price = money(as_decimal(variant.price))
        items_by_vendor[product.vendor_id].append(
            CheckoutItem(
                product_id=str(product.id),
                variant_id=str(variant.id),
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                total_price=money(unit_price * quantity),
            )
        )

    groups: list[CheckoutGroup] = []
    for vendor_id, items in items_by_vendor.items():
        subtotal = money(sum((item.total_price for item in items), Decimal("0.00")))
        tax_amount = money(subtotal * TAX_RATE)
        shipping_cost = money(SHIPPING_FEE[data.shipping_method])
        discount_amount = (
            money(subtotal * Decimal(coupon.discount_percent) / Decimal("100"))
            if coupon is not None
            else Decimal("0.00")
        )
        total = money(subtotal + tax_amount + shipping_cost - discount_amount)
        if total < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The checkout total cannot be negative.",
            )

        groups.append(
            CheckoutGroup(
                vendor_id=vendor_id,
                items=items,
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                discount_amount=discount_amount,
                total_amount=total,
            )
        )

    return groups, coupon
