from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from src.users.constants import USER_EMAIL, USER_IMG

router = APIRouter(tags=["User"], prefix="/users")
security = HTTPBearer(auto_error=False)


# ====================
# Schemas
# ====================


class UserProfile(BaseModel):
    img: str
    email: EmailStr
    name: str

    model_config = {
        "json_schema_extra": {
            "example": {"img": USER_IMG, "email": USER_EMAIL, "name": "John Doe"}
        }
    }


class UserProfileUpdate(BaseModel):
    name: str
    img: str

    model_config = {
        "json_schema_extra": {"example": {"name": "Jane Doe", "img": USER_IMG}}
    }


# ====================
# Routes
# ====================


@router.get(
    "/me",
    summary="View current user profile",
    description="Returns the currently authenticated user's profile using the Firebase Bearer token.",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User profile retrieved"},
        401: {"description": "Invalid or missing token"},
    },
)
async def get_profile(
    _creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserProfile:
    return UserProfile(img=USER_IMG, email=USER_EMAIL, name="Stub User")


@router.patch(
    "/me",
    summary="Update current user profile",
    description="Updates the name and image of the currently authenticated user using the Firebase Bearer token.",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User profile updated"},
        400: {"description": "Invalid request body"},
        401: {"description": "Invalid or missing token"},
        403: {"description": "User authenticated but not registered"},
    },
)
async def update_profile(
    _creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    _data: UserProfileUpdate,
) -> UserProfile:
    return UserProfile(img=_data.img, email=USER_EMAIL, name=_data.name)
