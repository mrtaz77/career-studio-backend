from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from test_util import api_prefix, get_firebase_token

from src.app import create_app
from src.auth.exceptions import UserNotFoundException
from src.users.constants import USER_NOT_FOUND
from src.users.exceptions import UsernameUnavailableException
from src.users.schemas import UserProfileUpdate
from src.users.service import get_user_profile_by_uid, update_user_profile


@pytest.fixture
def auth_headers():
    token = get_firebase_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_user_profile_crud_flow(client, auth_headers):
    # === Step 1: GET profile ===
    get_resp = client.get(f"{api_prefix}/users/me", headers=auth_headers)
    assert get_resp.status_code == 200
    original = get_resp.json()
    assert original["username"]

    # === Step 2: PATCH update profile ===
    updated_payload = {"full_name": "Updated Name", "address": "999 Updated Address"}
    patch_resp = client.patch(
        f"{api_prefix}/users/me", json=updated_payload, headers=auth_headers
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["full_name"] == "Updated Name"
    assert updated["address"] == "999 Updated Address"

    # === Step 3: Revert to original ===
    revert_payload = {
        "full_name": original["full_name"],
        "address": original["address"],
    }
    revert_resp = client.patch(
        f"{api_prefix}/users/me", json=revert_payload, headers=auth_headers
    )
    assert revert_resp.status_code == 200
    reverted = revert_resp.json()
    assert reverted["full_name"] == original["full_name"]
    assert reverted["address"] == original["address"]


def test_user_not_found_error(client, auth_headers, mocker):
    mocker.patch(
        "src.users.router.update_user_profile",
        side_effect=UserNotFoundException(),
    )

    response = client.patch(
        f"{api_prefix}/users/me", json={"username": "takenname"}, headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == USER_NOT_FOUND

    mocker.patch(
        "src.users.router.get_user_profile_by_uid",
        side_effect=UserNotFoundException(),
    )
    response = client.get(f"{api_prefix}/users/me", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == USER_NOT_FOUND


def test_username_unavailable_error(client, auth_headers, mocker):
    # Patch the actual reference used in the route
    mocker.patch(
        "src.users.router.update_user_profile",
        side_effect=UsernameUnavailableException(),
    )

    response = client.patch(
        f"{api_prefix}/users/me", json={"username": "takenname"}, headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Username is unavailable"


def test_invalid_phone_number_format_error(client, auth_headers):
    response = client.patch(
        f"{api_prefix}/users/me",
        json={"phone": "+120012301"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid phone number format"
    response = client.patch(
        f"{api_prefix}/users/me",
        json={"phone": "abc-1234"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid phone number format"


def test_invalid_phone_number_error(client, auth_headers):
    response = client.patch(
        f"{api_prefix}/users/me",
        json={"phone": "+abc-1234"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid phone number"


@pytest.mark.asyncio
async def test_get_user_profile_by_uid_user_not_found(mocker):
    fake_db = MagicMock()
    fake_db.user.find_unique = AsyncMock(return_value=None)

    @asynccontextmanager
    async def mock_get_db():
        yield fake_db

    mocker.patch("src.users.service.get_db", mock_get_db)

    with pytest.raises(UserNotFoundException):
        await get_user_profile_by_uid("nonexistent_uid")

    with pytest.raises(UserNotFoundException):
        await update_user_profile("nonexistent_uid", UserProfileUpdate())
