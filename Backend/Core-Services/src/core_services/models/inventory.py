import uuid
from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"

    inventory_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id: str = Field(max_length=24, index=True)  # Mongo ObjectId as hex
    variant_id: uuid.UUID
    vendor_id: uuid.UUID = Field(index=True)
    available_qty: int = Field(default=0, ge=0)
    sold_qty: int = Field(default=0, ge=0)
    last_restocked_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
