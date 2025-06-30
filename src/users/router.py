from logging import getLogger

from fastapi import APIRouter, Body, HTTPException, Request, status

from src.auth.exceptions import UserNotFoundException
from src.users.exceptions import (
    InvalidPhoneNumberException,
    InvalidPhoneNumberFormatException,
    UsernameUnavailableException,
)
from src.users.schemas import UserProfile, UserProfileUpdate
from src.users.service import get_user_profile_by_uid, update_user_profile

logger = getLogger(__name__)

router = APIRouter(tags=["User"], prefix="/users")

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
        404: {"description": "User not found"},
    },
)
async def get_profile(request: Request) -> UserProfile:
    try:
        uid = request.state.user.get("uid", "")
        user = await get_user_profile_by_uid(uid)
        return UserProfile(
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            img=user.img,
            address=user.address,
            phone=user.phone,
            updated_at=user.updated_at,
        )
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.patch(
    "/me",
    summary="Update current user profile",
    description="Updates the username, full_name, address, phone, or img of the currently authenticated user using the Firebase Bearer token. All fields are optional, but at least one must be provided. Username must be unique.",
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
    request: Request,
    data: UserProfileUpdate = Body(...),
) -> UserProfile:
    try:
        uid = request.state.user.get("uid", "")
        updated_user = await update_user_profile(uid, data)
        return updated_user
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except UsernameUnavailableException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except InvalidPhoneNumberException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except InvalidPhoneNumberFormatException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
