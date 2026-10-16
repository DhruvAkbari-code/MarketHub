from uuid import UUID

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_db_session, current_user
from core_services.models.product import Product
from core_services.models.user import User
from core_services.models.wishlist import Wishlist
from core_services.schemas.product_schema import ProductResponse, ProductVariantResponse
from core_services.schemas.wishlist_schema import WishlistAdd, WishlistItemResponse
from core_services.services import wishlist_service as svc

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.post("", response_model=Wishlist, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    payload: WishlistAdd,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_user),
):
    product = await Product.get(payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The product not found.")
    if not any(v.id == payload.variant_id and v.is_active for v in product.variants):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The variant not found.")
    return await svc.add(db, user.id, str(product.id), payload.variant_id)


@router.get("", response_model=list[WishlistItemResponse])
async def my_wishlist(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_user),
):
    rows = await svc.list_for_user(db, user.id)
    ids = {PydanticObjectId(r.product_id) for r in rows}
    products = await Product.find(
        {"_id": {"$in": list(ids)}, "is_active": True}
    ).to_list()
    by_id = {p.id: p for p in products}

    items = []
    for r in rows:
        product = by_id.get(PydanticObjectId(r.product_id))
        if not product:
            continue
        variant = next((v for v in product.variants if v.id == r.variant_id), None)
        if not variant:
            continue
        items.append(
            WishlistItemResponse(
                wishlist_id=r.wishlist_id,
                added_at=r.added_at,
                product_id=product.id,
                product_name=product.name,
                image_url=product.images[0].url if product.images else None,
                variant=ProductVariantResponse.model_validate(variant),
            )
        )
    return items


@router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    wishlist_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_user),
):
    await svc.remove(db, user.id, wishlist_id)
