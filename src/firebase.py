from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Optional

import firebase_admin
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError

from src.auth.constants import USER_NOT_AUTHENTICATED

__all__ = ["auth"]

logger = getLogger(__name__)
security = HTTPBearer()


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK with credentials from JSON file."""
    try:
        # Get the path to the credentials file
        current_dir = Path(__file__).parent
        credentials_path = current_dir.parent / "secrets" / "firebase-adminsdk.json"

        if not credentials_path.exists():
            logger.error(f"Firebase credentials file not found at {credentials_path}")
            raise FileNotFoundError(
                f"Firebase credentials file not found at {credentials_path}"
            )

        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(str(credentials_path))
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {str(e)}")


def get_firebase_auth() -> Optional[Any]:
    """Get Firebase Auth client instance."""
    try:
        # The firebase_admin.auth module does not have a Client class;
        # returning the module itself for compatibility.
        logger.debug("Firebase Auth client retrieved successfully")
        return auth
    except FirebaseError as e:
        logger.error(f"Failed to get Firebase Auth client: {str(e)}")
        raise RuntimeError(f"Failed to get Firebase Auth client: {str(e)}")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token.

    Args:
        token: Firebase ID token

    Returns:
        Dict containing decoded token claims

    Raises:
        ValueError: If token is invalid
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return dict(decoded_token)
    except FirebaseError as e:
        logger.error(f"Firebase token verification failed: {str(e)}")
        raise ValueError("Invalid token") from e


def get_user_by_uid(uid: str) -> Dict[str, Any]:
    """
    Get user data from Firebase by UID.

    Args:
        uid: Firebase user UID

    Returns:
        Dict containing user data

    Raises:
        ValueError: If user not found
    """
    try:
        user = auth.get_user(uid)
        # Convert UserRecord to dict
        user_dict = {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "phone_number": user.phone_number,
            "email_verified": user.email_verified,
            "disabled": user.disabled,
        }
        return user_dict
    except FirebaseError as e:
        logger.error(f"Failed to get user data: {str(e)}")
        raise ValueError("User not found") from e


def get_user_email(uid: str) -> str:
    """
    Get user email from Firebase by UID.

    Args:
        uid: Firebase user UID

    Returns:
        User's email address

    Raises:
        ValueError: If user not found
    """
    try:
        user = auth.get_user(uid)
        if not user.email:
            raise ValueError("User has no email")
        return str(user.email)
    except FirebaseError as e:
        logger.error(f"Failed to get user email: {str(e)}")
        raise ValueError("User not found") from e


async def verify_token_fastapi(
    credentials: HTTPAuthorizationCredentials,
) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return decoded token data.

    Args:
        credentials: HTTP Authorization credentials containing the token

    Returns:
        Dict containing the decoded token data

    Raises:
        HTTPException: If token is invalid or verification fails
    """
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        logger.debug(
            f"Token verified successfully for user: {decoded_token.get('email', 'unknown')}"
        )
        return dict(decoded_token)
    except ValueError as e:
        logger.warning(f"Invalid authentication token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except FirebaseError as e:
        logger.error(f"Error verifying authentication token: {str(e)}")
        raise HTTPException(
            status_code=401, detail="Error verifying authentication token"
        )


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency for getting the current authenticated user.
    This is now a wrapper around the middleware's state.

    Args:
        request: FastAPI request object

    Returns:
        Dict containing the user data from the decoded token

    Raises:
        HTTPException: If user is not authenticated
    """
    if not hasattr(request.state, "user"):
        logger.warning(USER_NOT_AUTHENTICATED)
        raise HTTPException(status_code=401, detail=USER_NOT_AUTHENTICATED)
    return dict(request.state.user)


async def get_current_uid(request: Request) -> str:
    """
    FastAPI dependency for getting the current user's UID.

    Args:
        request: FastAPI request object

    Returns:
        str: The user's UID

    Raises:
        HTTPException: If user is not authenticated
    """
    if not hasattr(request.state, "uid"):
        logger.warning(USER_NOT_AUTHENTICATED)
        raise HTTPException(status_code=401, detail=USER_NOT_AUTHENTICATED)
    return str(request.state.uid)


# Initialize Firebase when the module is imported
initialize_firebase()
