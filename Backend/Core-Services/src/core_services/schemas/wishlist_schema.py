from datetime import datetime
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel

from core_services.schemas.product_schema import ProductVariantResponse  # adjust


class WishlistAdd(BaseModel):
    product_id: PydanticObjectId
    variant_id: UUID


class WishlistItemResponse(BaseModel):
    wishlist_id: UUID
    added_at: datetime
    product_id: PydanticObjectId
    product_name: str
    image_url: str | None
    variant: ProductVariantResponse
