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
    profile_picture: str | None = None
    email_verified: bool


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
