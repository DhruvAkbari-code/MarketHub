import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    label: str = Field(max_length=30)
    full_name: str = Field(max_length=100)
    phone: str = Field(max_length=10)
    line1: str = Field(max_length=150)
    line2: str | None = Field(default=None, max_length=150)
    city: str = Field(max_length=60)
    state: str = Field(max_length=60)
    postal_code: str = Field(max_length=6)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
