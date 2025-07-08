from logging import getLogger

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from src.auth.exceptions import UserNotFoundException
from src.database import get_db
from src.users.exceptions import (
    InvalidPhoneNumberException,
    InvalidPhoneNumberFormatException,
    UsernameUnavailableException,
)
from src.users.schemas import UserProfile, UserProfileUpdate

logger = getLogger(__name__)


async def get_user_profile_by_uid(uid: str) -> UserProfile:
    """
    Get user data by UID.

    Args:
        uid: User UID

    Returns:
        UserCreate: User data

    Raises:
        ValueError: If user not found
    """
    async with get_db() as db:
        user = await db.user.find_unique(where={"uid": uid})
        if not user:
            raise UserNotFoundException()

        return UserProfile(
            username=user.username,
            email=user.email,
            img=user.img,
            full_name=user.full_name,
            address=user.address,
            phone=user.phone,
            updated_at=str(user.updated_at),
        )


async def update_user_profile(uid: str, update: UserProfileUpdate) -> UserProfile:
    """
    Update user profile.

    Args:
        uid: User UID
        update: UserProfileUpdate object containing fields to update

    Returns:
        UserProfile: Updated user profile

    Raises:
        UserNotFoundError: If user not found
        UsernameUnavailableException: If the new username is already taken
        InvalidPhoneNumberException: If the phone number cannot be parsed
        InvalidPhoneNumberFormatException: If phone number is invalid
    """
    async with get_db() as db:
        user = await db.user.find_unique(where={"uid": uid})
        if not user:
            raise UserNotFoundException()

        if update.phone and update.phone != user.phone:
            if not update.phone.startswith("+"):
                raise InvalidPhoneNumberFormatException()

            try:
                parsed = phonenumbers.parse(update.phone, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise InvalidPhoneNumberFormatException()
            except NumberParseException:
                raise InvalidPhoneNumberException()

        # Check username uniqueness if being changed
        if update.username and update.username != user.username:
            existing = await db.user.find_unique(where={"username": update.username})
            if existing and existing.uid != uid:
                raise UsernameUnavailableException()

        # Only update provided fields
        update_data = update.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return UserProfile(
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                img=user.img,
                address=user.address,
                phone=user.phone,
                updated_at=user.updated_at,
            )

        updated_user = await db.user.update(where={"uid": uid}, data=update_data)

        return UserProfile(
            username=updated_user.username,
            full_name=updated_user.full_name,
            email=updated_user.email,
            img=updated_user.img,
            address=updated_user.address,
            phone=updated_user.phone,
            updated_at=updated_user.updated_at,
        )
