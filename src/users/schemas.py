from datetime import datetime
from typing import Optional

import phonenumbers
from pydantic import BaseModel, EmailStr, field_validator


class UserProfile(BaseModel):
    """Schema for user profile data."""

    username: str
    full_name: Optional[str]
    email: EmailStr
    img: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile data."""

    username: Optional[str] = None
    full_name: Optional[str] = None
    img: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number format.")
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number.")
        return v
