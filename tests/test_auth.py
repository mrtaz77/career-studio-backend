from fastapi.testclient import TestClient
from test_util import api_prefix, get_firebase_token

from src.app import create_app


def test_signin_returns_200_or_201():
    app = create_app()
    with TestClient(app) as client:
        token = get_firebase_token()
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(f"{api_prefix}/auth/signin", headers=headers)

        assert response.status_code in (200, 201)
        assert "message" in response.json()
        assert response.json()["message"] in [
            "User signed in successfully",
            "User created and signed in",
        ]
