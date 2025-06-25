import pytest
from fastapi.testclient import TestClient
from test_util import api_prefix, get_firebase_token

from src.app import create_app
from src.users.exceptions import UsernameUnavailableException


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
