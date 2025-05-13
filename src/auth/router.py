from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

router = APIRouter(tags=["Auth"], prefix="/auth")

security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


# ====================
# Response Schemas
# ====================


class AuthResponse(BaseModel):
    message: str


# ====================
# Routes
# ====================


@router.post(
    "/signup",
    summary="Sign up with Bearer Firebase token",
    description="Creates a new user using the Firebase Bearer token sent in the Authorization header.",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User successfully created"},
        409: {"description": "User already exists"},
        401: {"description": "Invalid or missing token"},
    },
)
async def signup(
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> AuthResponse:
    """
    Expects: Bearer <Firebase Token> in the Authorization header.
    """
    # Stub logic for user creation
    return AuthResponse(message="Stub: User created")


@router.post(
    "/signin",
    summary="Sign in with Bearer Firebase token",
    description="Signs in an existing user using the Firebase Bearer token sent in the Authorization header.",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User successfully signed in"},
        401: {"description": "Invalid or missing token"},
        403: {"description": "User authenticated but not registered"},
    },
)
async def signin(
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> AuthResponse:
    """
    Expects: Bearer <Firebase Token> in the Authorization header.
    """
    # Stub logic for user sign-in
    return AuthResponse(message="Stub: User signed in")
