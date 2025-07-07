import secrets
from datetime import datetime
from logging import getLogger

from codename import codename  # type: ignore

from src.auth.exceptions import (
    EmailUnavailableException,
    UserAlreadyExistsError,
    UsernameUnavailableException,
)
from src.auth.schemas import SignupResponse, UserCreate
from src.database import get_db

logger = getLogger(__name__)


async def create_user(user_data: UserCreate) -> SignupResponse:
    """
    Create a new user in the database.

    Args:
        user_data: User data from Firebase token

    Returns:
        SignupResponse: Created user confirmation

    Raises:
        ValueError: If user already exists
    """

    async with get_db() as db:
        # Check if user already exists by UID
        existing_user = await db.user.find_unique(where={"uid": user_data.uid})
        if existing_user:
            raise UserAlreadyExistsError()

        # Check if username or email is already taken
        existing_username = await db.user.find_unique(
            where={"username": user_data.username}
        )
        if existing_username:
            raise UsernameUnavailableException()

        existing_email = await db.user.find_unique(where={"email": user_data.email})
        if existing_email:
            raise EmailUnavailableException()

        # Create new user
        await db.user.create(
            data={
                "username": user_data.username,
                "email": user_data.email,
                "img": user_data.img,
                "uid": user_data.uid,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

        return SignupResponse(
            username=user_data.username, message="User created successfully"
        )


async def get_user_by_uid(uid: str) -> UserCreate:
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
            raise ValueError("User not found")

        return UserCreate(
            username=user.username,
            email=user.email,
            img=user.img,
            uid=user.uid,
        )


async def generate_username() -> str:
    username = f"{codename(separator='_')}_{100 + secrets.randbelow(900)}"
    async with get_db() as db:
        while await db.user.find_unique(where={"username": username}):
            username = f"{codename(separator='_')}_{100 + secrets.randbelow(900)}"
    return username
