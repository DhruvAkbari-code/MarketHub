import uuid
from enum import Enum
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class VendorStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class VendorProfile(SQLModel, table=True):
    __tablename__ = "vendors"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    store_name: str = Field(max_length=100)
    category: str = Field(max_length=50)
    website: str | None = Field(default=None, max_length=255)
    about: str = Field(max_length=1000)
    status: VendorStatus = Field(default=VendorStatus.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
