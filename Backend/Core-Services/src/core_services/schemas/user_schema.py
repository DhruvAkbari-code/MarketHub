import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator
from core_services.models.user import Role


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    phone: str | None = None
    profile_picture: str | None = None
    email_verified: bool
    role: Role


class UpdateProfileRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    phone: str | None = Field(default=None, pattern=r"^[0-9]{10}$")

    @field_validator("phone", mode="before")
    @classmethod
    def empty_phone_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class AddressRequest(BaseModel):
    label: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^[0-9]{10}$")
    line1: str = Field(min_length=3, max_length=150)
    line2: str | None = Field(default=None, max_length=150)
    city: str = Field(min_length=2, max_length=60)
    state: str = Field(min_length=2, max_length=60)
    postal_code: str = Field(pattern=r"^[0-9]{6}$")
    is_default: bool = False


class AddressResponse(AddressRequest):
    id: uuid.UUID
