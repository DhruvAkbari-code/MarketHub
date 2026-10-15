from datetime import datetime
from decimal import Decimal

from bson.decimal128 import Decimal128
from pydantic import field_validator
from typing import Annotated
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

Money = Annotated[Decimal, Field(max_digits=12, decimal_places=2)]


# for Images
class ImageUpdate(BaseModel):
    alt: str | None = Field(default=None, max_length=200)


class ImageReorder(BaseModel):
    image_ids: list[UUID]


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    alt: str | None
    order: int


# for Variants
class ProductVariantCreate(BaseModel):
    options: dict[str, str] = Field(default_factory=dict)
    price: Money = Field(gt=0)


class ProductVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    options: dict[str, str]
    price: Money
    is_active: bool


# for Product
class ProductCreate(BaseModel):
    category_id: PydanticObjectId
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    variants: list[ProductVariantCreate] = Field(min_length=1)


class ProductUpdate(BaseModel):
    category_id: PydanticObjectId | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    vendor_id: UUID
    category_id: PydanticObjectId
    name: str
    description: str | None
    images: list[ProductImageResponse]
    variants: list[ProductVariantResponse]
    is_active: bool
    created_at: datetime
    updated_at: datetime
