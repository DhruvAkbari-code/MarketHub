from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import current_user, get_db_session
from core_services.models.product import Product
from core_services.models.user import User
from core_services.schemas.cart_schema import CartAdd, CartResponse, CartUpdate
from core_services.services import cart_service as svc

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    db: AsyncSession = Depends(get_db_session), user: User = Depends(current_user)
):
    return await svc.build_response(db, await svc.load(user.id))


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    payload: CartAdd,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_user),
):
    product = await Product.get(payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The product not found.")
    if not any(v.id == payload.variant_id and v.is_active for v in product.variants):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The variant not found.")

    variant_id = str(payload.variant_id)
    cart = await svc.load(user.id)
    line = svc.find_line(cart, variant_id)
    wanted = (line["quantity"] if line else 0) + payload.quantity
    if wanted > await svc.available_stock(db, str(product.id), payload.variant_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Not enough stock available.")

    cart = await svc.add_item(user.id, str(product.id), variant_id, payload.quantity)
    return await svc.build_response(db, cart)


@router.patch("/items/{variant_id}", response_model=CartResponse)
async def update_item(
    variant_id: UUID,
    payload: CartUpdate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_user),
):
    cart = await svc.load(user.id)
    line = svc.find_line(cart, str(variant_id))
    if not line:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not in your cart.")
    if payload.quantity > await svc.available_stock(db, line["product_id"], variant_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Not enough stock available.")

    cart = await svc.set_quantity(user.id, str(variant_id), payload.quantity)
    return await svc.build_response(db, cart)


@router.delete("/items/{variant_id}", response_model=CartResponse)
async def remove_item(
    variant_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_user),
):
    if not await svc.remove_item(user.id, str(variant_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not in your cart.")
    return await svc.build_response(db, await svc.load(user.id))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user: User = Depends(current_user)):
    await svc.clear(user.id)
