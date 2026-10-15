from datetime import datetime, timezone

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, TEXT


class Category(Document):
    name: str = Field(max_length=100)
    slug: Indexed(str, unique=True)
    parent_id: PydanticObjectId | None = None
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "categories"
        indexes = [
            IndexModel([("name", TEXT)]),
            "parent_id",
            "is_active",
        ]
