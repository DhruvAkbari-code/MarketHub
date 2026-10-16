import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from beanie import PydanticObjectId
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.models.inventory import Inventory
from core_services.models.product import Product
from core_services.redis_client import redis_client
from core_services.schemas.cart_schema import CartLine, CartResponse

CART_TTL = 60 * 60 * 24 * 30


def _key(user_id: UUID) -> str:
    return f"cart:{user_id}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def load(user_id: UUID) -> dict:
    raw = await redis_client.get(_key(user_id))
    return json.loads(raw) if raw else {"items": [], "updated_at": None}


async def save(user_id: UUID, cart: dict) -> dict:
    cart["updated_at"] = _now()
    await redis_client.set(_key(user_id), json.dumps(cart), ex=CART_TTL)
    return cart


def find_line(cart: dict, variant_id: str) -> dict | None:
    return next((i for i in cart["items"] if i["variant_id"] == variant_id), None)


async def available_stock(db: AsyncSession, product_id: str, variant_id: UUID) -> int:
    result = await db.exec(
        select(Inventory.available_qty).where(
            Inventory.product_id == product_id, Inventory.variant_id == variant_id
        )
    )
    return result.first() or 0


async def add_item(
    user_id: UUID, product_id: str, variant_id: str, quantity: int
) -> dict:
    cart = await load(user_id)
    line = find_line(cart, variant_id)
    if line:
        line["quantity"] += quantity
    else:
        cart["items"].append(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "quantity": quantity,
                "added_at": _now(),
            }
        )
    return await save(user_id, cart)


async def set_quantity(user_id: UUID, variant_id: str, quantity: int) -> dict | None:
    cart = await load(user_id)
    line = find_line(cart, variant_id)
    if not line:
        return None
    line["quantity"] = quantity
    return await save(user_id, cart)


async def remove_item(user_id: UUID, variant_id: str) -> bool:
    cart = await load(user_id)
    before = len(cart["items"])
    cart["items"] = [i for i in cart["items"] if i["variant_id"] != variant_id]
    if len(cart["items"]) == before:
        return False
    await save(user_id, cart)
    return True


async def clear(user_id: UUID) -> None:
    await redis_client.delete(_key(user_id))


async def build_response(db: AsyncSession, cart: dict) -> CartResponse:
    """Prices, names and totals all come from MongoDB/Postgres, never from the client."""
    ids = {PydanticObjectId(i["product_id"]) for i in cart["items"]}
    products = await Product.find(
        {"_id": {"$in": list(ids)}, "is_active": True}
    ).to_list()
    by_id = {p.id: p for p in products}

    lines: list[CartLine] = []
    for item in cart["items"]:
        product = by_id.get(PydanticObjectId(item["product_id"]))
        if not product:
            continue
        variant = next(
            (
                v
                for v in product.variants
                if str(v.id) == item["variant_id"] and v.is_active
            ),
            None,
        )
        if not variant:
            continue
        qty = item["quantity"]
        stock = await available_stock(db, item["product_id"], variant.id)
        lines.append(
            CartLine(
                product_id=item["product_id"],
                variant_id=item["variant_id"],
                name=product.name,
                image_url=product.images[0].url if product.images else None,
                options=variant.options,
                unit_price=variant.price,
                quantity=qty,
                line_total=variant.price * qty,
                in_stock=stock >= qty,
            )
        )

    return CartResponse(
        items=lines,
        total_items=sum(l.quantity for l in lines),
        subtotal=sum((l.line_total for l in lines), Decimal("0")),
        updated_at=cart["updated_at"],
    )
