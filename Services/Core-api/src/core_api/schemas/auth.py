import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


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
