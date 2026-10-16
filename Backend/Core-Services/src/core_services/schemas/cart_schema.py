from datetime import datetime
from decimal import Decimal
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class CartAdd(BaseModel):
    product_id: PydanticObjectId
    variant_id: UUID
    quantity: int = Field(default=1, ge=1, le=20)


class CartUpdate(BaseModel):
    quantity: int = Field(ge=1, le=20)


class CartLine(BaseModel):
    product_id: str
    variant_id: str
    name: str
    image_url: str | None
    options: dict[str, str]
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    in_stock: bool


class CartResponse(BaseModel):
    items: list[CartLine]
    total_items: int
    subtotal: Decimal
    updated_at: datetime | None
