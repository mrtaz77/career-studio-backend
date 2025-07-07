from logging import getLogger

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.security import HTTPBearer

from src.auth.exceptions import UserAlreadyExistsError
from src.auth.schemas import AuthResponse, SignupResponse, UserCreate
from src.auth.service import create_user, generate_username, get_user_by_uid

logger = getLogger(__name__)

router = APIRouter(tags=["Auth"], prefix="/auth")

security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


# ====================
# Routes
# ====================


@router.post(
    "/signup",
    summary="Sign up with Bearer Firebase token",
    description="Creates a new user using the Firebase Bearer token sent in the Authorization header.",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User successfully created"},
        409: {"description": "User already exists"},
        401: {"description": "Invalid or missing token"},
    },
)
async def signup(request: Request) -> SignupResponse:
    """
    Sign up a new user using Firebase authentication.

    Args:
        request: FastAPI request object containing user data from Firebase token

    Returns:
        SignupResponse: Created user confirmation
    """
    try:
        username = request.state.user.get("name")
        if not username:
            username = await generate_username()

        user_data = UserCreate(
            username=username,
            email=request.state.user.get("email", ""),
            img=request.state.user.get("picture"),
            uid=request.state.user.get("uid", ""),
        )
        return await create_user(user_data)

    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post(
    "/signin",
    summary="Sign in with Bearer Firebase token",
    description="Signs in an existing user using the Firebase Bearer token sent in the Authorization header. If the user does not exist, creates a new user.",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User successfully signed in"},
        201: {"description": "User created and signed in"},
        401: {"description": "Invalid or missing token"},
    },
)
async def signin(
    request: Request,
) -> AuthResponse:
    """
    Signs in an existing user or creates a new user if not found.
    Expects: Bearer <Firebase Token> in the Authorization header.
    """
    try:
        uid = request.state.user.get("uid", "")
        user = await get_user_by_uid(uid)
        if user:
            return AuthResponse(message="User signed in successfully")
        user_data = UserCreate(
            username=request.state.user.get("name", ""),
            email=request.state.user.get("email", ""),
            img=request.state.user.get("picture"),
            uid=uid,
        )
        await create_user(user_data)
        return AuthResponse(message="User created and signed in")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
