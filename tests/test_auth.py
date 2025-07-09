from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from test_util import api_prefix

from src.app import create_app
from src.auth.exceptions import (
    EmailUnavailableException,
    UserAlreadyExistsError,
    UsernameUnavailableException,
)
from src.auth.schemas import SignupResponse, UserCreate
from src.auth.service import create_user, generate_username, get_user_by_uid


class TestAuthEndpoints:
    """Integration tests for auth endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app()
        with TestClient(app) as c:
            yield c

    @pytest.fixture
    def mock_firebase_user_data(self):
        return {
            "uid": "test_uid_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg",
        }

    def test_signin_without_auth_header_returns_401(self, client):
        """Test signin without authorization header returns 401."""
        response = client.post(f"{api_prefix}/auth/signin")

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signin_with_invalid_token_returns_401(self, client):
        """Test signin with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid_token"}

        response = client.post(f"{api_prefix}/auth/signin", headers=headers)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signup_user_already_exists_returns_409(self, client):
        """Test signup when user already exists returns 409."""
        headers = {"Authorization": "Bearer fake_existing_user_token"}

        # Mock Firebase auth verification to return our test user data
        mock_decoded_token = {
            "uid": "existing_user_uid_123",
            "email": "existing@example.com",
            "name": "Existing User",
            "picture": "https://example.com/existing.jpg",
        }

        with patch("src.auth.service.create_user") as mock_create_user, patch(
            "src.firebase.auth.verify_id_token", return_value=mock_decoded_token
        ):

            mock_create_user.side_effect = UserAlreadyExistsError()

            response = client.post(f"{api_prefix}/auth/signup", headers=headers)

            assert response.status_code == 409
            assert "detail" in response.json()

    def test_signup_username_unavailable_returns_409(self, client):
        """Test signup when username is unavailable returns 409."""
        headers = {"Authorization": "Bearer fake_username_collision_token"}

        # Mock Firebase auth verification to return our test user data
        mock_decoded_token = {
            "uid": "new_user_uid_456",
            "email": "newuser2@example.com",
            "name": "taken_username",  # This username will be taken
            "picture": "https://example.com/user2.jpg",
        }

        with patch("src.auth.service.create_user") as mock_create_user, patch(
            "src.firebase.auth.verify_id_token", return_value=mock_decoded_token
        ):

            mock_create_user.side_effect = UsernameUnavailableException()

            response = client.post(f"{api_prefix}/auth/signup", headers=headers)

            assert response.status_code == 409
            assert "detail" in response.json()

    def test_signup_email_unavailable_returns_409(self, client):
        """Test signup when email is unavailable returns 409."""
        headers = {"Authorization": "Bearer fake_email_collision_token"}

        # Mock Firebase auth verification to return our test user data
        mock_decoded_token = {
            "uid": "new_user_uid_789",
            "email": "taken@example.com",  # This email will be taken
            "name": "New User With Taken Email",
            "picture": "https://example.com/user3.jpg",
        }

        with patch("src.auth.service.create_user") as mock_create_user, patch(
            "src.firebase.auth.verify_id_token", return_value=mock_decoded_token
        ):

            mock_create_user.side_effect = EmailUnavailableException()

            response = client.post(f"{api_prefix}/auth/signup", headers=headers)

            assert response.status_code == 409
            assert "detail" in response.json()

    def test_signin_service_error_returns_401(self, client):
        """Test signin when service throws unexpected error returns 401."""
        headers = {"Authorization": "Bearer fake_service_error_token"}

        # Mock Firebase auth verification to return our test user data
        mock_decoded_token = {
            "uid": "service_error_uid_789",
            "email": "serviceerror@example.com",
            "name": "Service Error User",
            "picture": "https://example.com/error.jpg",
        }

        with patch("src.auth.service.get_user_by_uid") as mock_get_user, patch(
            "src.firebase.auth.verify_id_token", return_value=mock_decoded_token
        ):

            # Mock unexpected ValueError (different from "User not found")
            mock_get_user.side_effect = ValueError("Database connection error")

            response = client.post(f"{api_prefix}/auth/signin", headers=headers)

            assert response.status_code == 401
            assert "detail" in response.json()

    def test_signup_without_auth_header_returns_401(self, client):
        """Test signup without authorization header returns 401."""
        response = client.post(f"{api_prefix}/auth/signup")

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signup_with_invalid_token_returns_401(self, client):
        """Test signup with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid_token"}

        response = client.post(f"{api_prefix}/auth/signup", headers=headers)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signin_with_malformed_auth_header_returns_401(self, client):
        """Test signin with malformed authorization header returns 401."""
        headers = {"Authorization": "NotBearer invalid_token"}

        response = client.post(f"{api_prefix}/auth/signin", headers=headers)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signup_with_malformed_auth_header_returns_401(self, client):
        """Test signup with malformed authorization header returns 401."""
        headers = {"Authorization": "NotBearer invalid_token"}

        response = client.post(f"{api_prefix}/auth/signup", headers=headers)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signin_unexpected_exception_handling(self, client):
        """Test signin handles unexpected exceptions gracefully."""
        headers = {"Authorization": "Bearer fake_exception_test_token"}

        # Mock Firebase auth verification to return our test user data
        mock_decoded_token = {
            "uid": "exception_test_uid",
            "email": "exception@example.com",
            "name": "Exception Test User",
            "picture": "https://example.com/exception.jpg",
        }

        with patch("src.auth.service.get_user_by_uid") as mock_get_user, patch(
            "src.auth.service.create_user"
        ) as mock_create_user, patch(
            "src.firebase.auth.verify_id_token", return_value=mock_decoded_token
        ):

            # Mock get_user_by_uid to raise ValueError (user not found)
            mock_get_user.side_effect = ValueError("User not found")
            # Mock create_user to raise an unexpected exception
            mock_create_user.side_effect = Exception("Database connection failed")

            response = client.post(f"{api_prefix}/auth/signin", headers=headers)

            # The signin route should catch ValueError but let other exceptions bubble up
            # which would result in a 500 error handled by FastAPI
            assert response.status_code in [401, 500]


class TestAuthService:
    """Unit tests for auth service functions."""

    @pytest.fixture
    def mock_db(self):
        """Mock database context manager."""
        mock_db = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_db
        mock_context.__aexit__.return_value = None
        return mock_db, mock_context

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db):
        """Test successful user creation."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no existing user
            db_instance.user.find_unique.return_value = None
            db_instance.user.create.return_value = None

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            result = await create_user(user_data)

            assert isinstance(result, SignupResponse)
            assert result.username == "testuser"
            assert result.message == "User created successfully"
            db_instance.user.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_already_exists_by_uid(self, mock_db):
        """Test user creation when user already exists by UID."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock existing user by UID
            existing_user = MagicMock()
            existing_user.uid = "test_uid"
            db_instance.user.find_unique.return_value = existing_user

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            with pytest.raises(UserAlreadyExistsError):
                await create_user(user_data)

    @pytest.mark.asyncio
    async def test_create_user_username_unavailable(self, mock_db):
        """Test user creation when username is unavailable."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no user by UID, but existing username
            existing_user = MagicMock()
            existing_user.username = "testuser"

            def mock_find_unique(where):
                if "uid" in where:
                    return None  # No user by UID
                elif "username" in where:
                    return existing_user  # Username taken
                return None

            db_instance.user.find_unique.side_effect = mock_find_unique

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            with pytest.raises(UsernameUnavailableException):
                await create_user(user_data)

    @pytest.mark.asyncio
    async def test_create_user_email_unavailable(self, mock_db):
        """Test user creation when email is unavailable."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no user by UID or username, but existing email
            existing_user = MagicMock()
            existing_user.email = "test@example.com"

            def mock_find_unique(where):
                if "uid" in where or "username" in where:
                    return None
                elif "email" in where:
                    return existing_user  # Email taken
                return None

            db_instance.user.find_unique.side_effect = mock_find_unique

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            with pytest.raises(EmailUnavailableException):
                await create_user(user_data)

    @pytest.mark.asyncio
    async def test_get_user_by_uid_success(self, mock_db):
        """Test successful user retrieval by UID."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock existing user
            mock_user = MagicMock()
            mock_user.username = "testuser"
            mock_user.email = "test@example.com"
            mock_user.uid = "test_uid"
            mock_user.img = None

            db_instance.user.find_unique.return_value = mock_user

            result = await get_user_by_uid("test_uid")

            assert isinstance(result, UserCreate)
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            assert result.uid == "test_uid"

    @pytest.mark.asyncio
    async def test_get_user_by_uid_not_found(self, mock_db):
        """Test user retrieval when user not found."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no user found
            db_instance.user.find_unique.return_value = None

            with pytest.raises(ValueError, match="User not found"):
                await get_user_by_uid("nonexistent_uid")

    @pytest.mark.asyncio
    async def test_generate_username_unique(self, mock_db):
        """Test username generation creates unique username."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context), patch(
            "src.auth.service.codename", return_value="test_code"
        ), patch("src.auth.service.secrets.randbelow", return_value=123):

            # Mock no existing user with generated username
            db_instance.user.find_unique.return_value = None

            result = await generate_username()

            assert result == "test_code_223"  # Expected: 100 + 123
            db_instance.user.find_unique.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_username_collision_retry(self, mock_db):
        """Test username generation retries on collision."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context), patch(
            "src.auth.service.codename", side_effect=["taken_name", "unique_name"]
        ), patch("src.auth.service.secrets.randbelow", side_effect=[123, 456]):

            # Mock first username exists, second doesn't
            existing_user = MagicMock()
            db_instance.user.find_unique.side_effect = [existing_user, None]

            result = await generate_username()

            assert result == "unique_name_556"  # 100 + 456
            assert db_instance.user.find_unique.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_username_multiple_collisions(self, mock_db):
        """Test username generation handles multiple collisions."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context), patch(
            "src.auth.service.codename", side_effect=["taken1", "taken2", "unique"]
        ), patch("src.auth.service.secrets.randbelow", side_effect=[111, 222, 333]):

            # Mock first two usernames exist, third doesn't
            existing_user = MagicMock()
            db_instance.user.find_unique.side_effect = [
                existing_user,
                existing_user,
                None,
            ]

            result = await generate_username()

            assert result == "unique_433"  # 100 + 333
            assert db_instance.user.find_unique.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_username_database_error(self, mock_db):
        """Test username generation handles database errors."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context), patch(
            "src.auth.service.codename", return_value="test_code"
        ), patch("src.auth.service.secrets.randbelow", return_value=123):

            # Mock database error
            db_instance.user.find_unique.side_effect = Exception(
                "Database connection error"
            )

            with pytest.raises(Exception, match="Database connection error"):
                await generate_username()

    @pytest.mark.asyncio
    async def test_create_user_database_create_error(self, mock_db):
        """Test create_user handles database creation errors."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no existing users but database creation fails
            db_instance.user.find_unique.return_value = None
            db_instance.user.create.side_effect = Exception("Database write error")

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            with pytest.raises(Exception, match="Database write error"):
                await create_user(user_data)

    @pytest.mark.asyncio
    async def test_create_user_with_image(self, mock_db):
        """Test create_user with image data."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no existing user
            db_instance.user.find_unique.return_value = None
            db_instance.user.create.return_value = None

            user_data = UserCreate(
                username="testuser",
                email="test@example.com",
                uid="test_uid",
                img="https://example.com/avatar.jpg",
            )

            result = await create_user(user_data)

            assert isinstance(result, SignupResponse)
            assert result.username == "testuser"
            assert result.message == "User created successfully"

            # Verify user.create was called with correct data including image
            create_call_args = db_instance.user.create.call_args[1]["data"]
            assert create_call_args["img"] == "https://example.com/avatar.jpg"
            assert create_call_args["username"] == "testuser"
            assert create_call_args["email"] == "test@example.com"
            assert create_call_args["uid"] == "test_uid"

    @pytest.mark.asyncio
    async def test_get_user_by_uid_with_image(self, mock_db):
        """Test get_user_by_uid returns user with image data."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock existing user with image
            mock_user = MagicMock()
            mock_user.username = "testuser"
            mock_user.email = "test@example.com"
            mock_user.uid = "test_uid"
            mock_user.img = "https://example.com/profile.jpg"

            db_instance.user.find_unique.return_value = mock_user

            result = await get_user_by_uid("test_uid")

            assert isinstance(result, UserCreate)
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            assert result.uid == "test_uid"
            assert result.img == "https://example.com/profile.jpg"

    @pytest.mark.asyncio
    async def test_get_user_by_uid_database_error(self, mock_db):
        """Test get_user_by_uid handles database errors."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock database error
            db_instance.user.find_unique.side_effect = Exception(
                "Database connection error"
            )

            with pytest.raises(Exception, match="Database connection error"):
                await get_user_by_uid("test_uid")

    @pytest.mark.asyncio
    async def test_create_user_empty_username_allowed(self, mock_db):
        """Test create_user allows empty username (router handles generation)."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no existing users
            db_instance.user.find_unique.return_value = None
            db_instance.user.create.return_value = None

            user_data = UserCreate(
                username="",  # Empty username should be allowed
                email="test@example.com",
                uid="test_uid",
                img=None,
            )

            result = await create_user(user_data)

            assert isinstance(result, SignupResponse)
            assert result.username == ""  # Service doesn't modify username
            assert result.message == "User created successfully"
            db_instance.user.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_none_image_handling(self, mock_db):
        """Test create_user handles None image correctly."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no existing user
            db_instance.user.find_unique.return_value = None
            db_instance.user.create.return_value = None

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            result = await create_user(user_data)

            assert isinstance(result, SignupResponse)

            # Verify user.create was called with None for img
            create_call_args = db_instance.user.create.call_args[1]["data"]
            assert create_call_args["img"] is None

    @pytest.mark.asyncio
    async def test_generate_username_format_validation(self, mock_db):
        """Test generate_username creates correctly formatted username."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context), patch(
            "src.auth.service.codename", return_value="cool_name"
        ), patch("src.auth.service.secrets.randbelow", return_value=42):

            # Mock no existing user with generated username
            db_instance.user.find_unique.return_value = None

            result = await generate_username()

            # Verify format: codename_number where number is 100-999
            assert result == "cool_name_142"  # 100 + 42
            assert "_" in result
            parts = result.split("_")
            assert len(parts) >= 2
            assert parts[-1].isdigit()
            number = int(parts[-1])
            assert 100 <= number <= 999

    @pytest.mark.asyncio
    async def test_get_user_by_uid_empty_string(self, mock_db):
        """Test get_user_by_uid with empty UID string."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Mock no user found with empty UID
            db_instance.user.find_unique.return_value = None

            with pytest.raises(ValueError, match="User not found"):
                await get_user_by_uid("")

    @pytest.mark.asyncio
    async def test_create_user_duplicate_check_order(self, mock_db):
        """Test create_user checks duplicates in correct order (UID, username, email)."""
        db_instance, db_context = mock_db

        with patch("src.auth.service.get_db", return_value=db_context):
            # Setup to test the order of checks
            existing_user = MagicMock()

            # First call (UID check) returns existing user
            db_instance.user.find_unique.return_value = existing_user

            user_data = UserCreate(
                username="testuser", email="test@example.com", uid="test_uid", img=None
            )

            with pytest.raises(UserAlreadyExistsError):
                await create_user(user_data)

            # Verify only UID check was made (should fail fast)
            assert db_instance.user.find_unique.call_count == 1
            call_args = db_instance.user.find_unique.call_args[1]["where"]
            assert "uid" in call_args
            assert call_args["uid"] == "test_uid"
