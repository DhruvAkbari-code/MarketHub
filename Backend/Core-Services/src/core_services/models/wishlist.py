import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class Wishlist(SQLModel, table=True):
    __tablename__ = "wishlist"
    __table_args__ = (UniqueConstraint("user_id", "product_id", "variant_id"),)

    wishlist_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    product_id: str = Field(max_length=24)  # Mongo ObjectId as hex
    variant_id: uuid.UUID
    added_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
