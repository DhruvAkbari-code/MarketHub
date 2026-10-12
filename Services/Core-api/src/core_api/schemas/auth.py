import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator
from core_api.models.user import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = Field(default=None, pattern=r"^\+?[1-9]\d{7,14}$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class RegisterResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    message: str = (
        "Registration successful. Please check your email to verify your account."
    )


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=10)


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(min_length=20)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    phone: str | None = None
    profile_picture: str | None = None
    email_verified: bool
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    new_password: str = Field(min_length=8, max_length=72)


class VendorRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = Field(default=None, pattern=r"^\+?[1-9]\d{7,14}$")
    # store
    store_name: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=50)
    website: str | None = Field(default=None, max_length=255)
    about: str = Field(min_length=10, max_length=1000)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UpdateProfileRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
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
