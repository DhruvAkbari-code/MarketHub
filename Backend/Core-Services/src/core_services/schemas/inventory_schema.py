from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: PydanticObjectId
    variant_id: UUID
    quantity: int = Field(ge=0)


class StockAdd(BaseModel):
    quantity: int = Field(gt=0)
