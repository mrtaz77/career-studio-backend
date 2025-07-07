from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


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
    file: Optional[str] = None
