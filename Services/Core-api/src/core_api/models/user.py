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
