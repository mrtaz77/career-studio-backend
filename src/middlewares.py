from logging import getLogger
from typing import Awaitable, Callable

from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.auth.constants import (
    AUTH_HEADER_MISSING,
    INVALID_TOKEN,
    TOKEN_VERIFICATION_ERROR,
)
from src.firebase import auth, verify_token

logger = getLogger(__name__)

security = HTTPBearer(auto_error=False)


class LimitBodySizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        body = await request.body()
        if len(body) > self.max_bytes:
            return Response("Payload too large", status_code=413)
        return await call_next(request)


async def verify_token_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Middleware to verify Firebase token in request header.

    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain

    Returns:
        Response from next handler

    Raises:
        HTTPException: If token is invalid or missing
    """
    try:
        # Skip token verification for certain paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise ValueError("No authorization header")

        # Verify token
        token = auth_header.split(" ")[1]
        user_data = verify_token(token)

        # Add user data to request state
        request.state.user = user_data

        return await call_next(request)

    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        # Ensure Response content is a string or bytes, not a dict
        return Response(
            content='{"detail": "Invalid or missing token"}',
            status_code=401,
            media_type="application/json",
        )


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Firebase authentication and set user UID in request state."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and set user UID in request state if authenticated."""
        try:
            logger.info(f"Processing request: {request.url.path}")
            # Skip authentication for certain paths
            if request.url.path in [
                "/api/v1/docs",
                "/api/v1/redoc",
                "/api/v1/openapi.json",
                "/openapi.json",
                "/favicon.ico",
                "/",
            ]:
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if not auth_header:
                logger.warning(AUTH_HEADER_MISSING)
                raise HTTPException(status_code=401, detail=AUTH_HEADER_MISSING)

            # Remove 'Bearer ' prefix if present
            token = auth_header.replace("Bearer ", "")
            decoded_token = auth.verify_id_token(token)

            # Set user data in request state
            request.state.user = decoded_token
            request.state.uid = decoded_token.get("uid")

            # Process the request
            response = await call_next(request)
            return response

        except ValueError:
            logger.warning(INVALID_TOKEN)
            raise HTTPException(status_code=401, detail=INVALID_TOKEN)
        except Exception as e:
            logger.error(f"{TOKEN_VERIFICATION_ERROR}: {str(e)}")
            raise HTTPException(status_code=401, detail=TOKEN_VERIFICATION_ERROR)
