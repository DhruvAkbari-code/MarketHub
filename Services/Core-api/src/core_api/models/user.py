import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, Enum):
    admin = "admin"
    customer = "customer"
    vendor = "vendor"
    support = "support"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    google_user_id: str | None = Field(
        default=None, max_length=255, unique=True, index=True
    )
    username: str = Field(max_length=50, index=True)
    password_hash: str | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=20)
    role: Role = Field(default=Role.customer)
    profile_picture: str | None = Field(default=None)
    email_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    last_login_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    created_at: datetime | None = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utcnow},
    )


class VendorStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class VendorProfile(SQLModel, table=True):
    __tablename__ = "vendor_profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)
    store_name: str = Field(max_length=100)
    category: str = Field(max_length=50)
    website: str | None = Field(default=None, max_length=255)
    about: str = Field(max_length=1000)
    status: VendorStatus = Field(default=VendorStatus.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
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
