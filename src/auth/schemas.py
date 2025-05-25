from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base schema for user data."""

    username: str
    email: EmailStr
    img: str | None = None
    uid: str


class UserCreate(UserBase):
    """Schema for user creation."""

    pass


class UserResponse(UserBase):
    """Schema for user response."""

    pass


class SignupResponse(BaseModel):
    """Schema for signup response."""

    username: str
    message: str


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    message: str
