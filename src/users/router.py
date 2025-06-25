from logging import getLogger

from fastapi import APIRouter, Body, HTTPException, Request, status

from src.auth.exceptions import UserNotFoundError
from src.users.exceptions import UsernameUnavailableException
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
    },
)
async def get_profile(request: Request) -> UserProfile:
    try:
        uid = request.state.user.get("uid", "")
        user = await get_user_profile_by_uid(uid)
        if user:
            return UserProfile(
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                img=user.img,
                address=user.address,
                phone=user.phone,
                updated_at=user.updated_at,
            )
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


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
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UsernameUnavailableException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
