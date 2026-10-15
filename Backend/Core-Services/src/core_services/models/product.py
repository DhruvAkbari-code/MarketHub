from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated
from uuid import UUID, uuid4

from beanie import Document, PydanticObjectId
from bson.decimal128 import Decimal128
from pydantic import BaseModel, Field, field_validator
from pymongo import ASCENDING, TEXT, IndexModel

Money = Annotated[Decimal, Field(max_digits=12, decimal_places=2)]


class ProductImage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str
    public_id: str
    alt: str | None = Field(default=None, max_length=200)
    order: int = Field(default=0, ge=0)


class ProductVariant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    options: dict[str, str] = Field(default_factory=dict)
    price: Money = Field(gt=0)
    is_active: bool = True

    @field_validator("price", mode="before")
    @classmethod
    def convert_decimal128(cls, value: Any) -> Any:
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value


class Product(Document):
    vendor_id: UUID
    category_id: PydanticObjectId
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    images: list[ProductImage] = Field(default_factory=list, max_length=10)
    variants: list[ProductVariant] = Field(min_length=1)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "products"
        indexes = [
            IndexModel([("category_id", ASCENDING), ("is_active", ASCENDING)]),
            IndexModel([("vendor_id", ASCENDING), ("is_active", ASCENDING)]),
            IndexModel([("name", TEXT), ("description", TEXT)], name="product_text"),
        ]
