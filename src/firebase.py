from logging import getLogger
from pathlib import Path
from typing import Any, Dict

import firebase_admin
from fastapi.security import HTTPBearer
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError

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
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {str(e)}")


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


# Initialize Firebase when the module is imported
initialize_firebase()
