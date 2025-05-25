from datetime import datetime
from logging import getLogger

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
        # Check if user already exists
        existing_user = await db.user.find_unique(where={"uid": user_data.uid})
        if existing_user:
            raise ValueError("User already exists")

        logger.debug(f"Creating new user with username: {user_data.username}")
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
