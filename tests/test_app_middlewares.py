from fastapi.testclient import TestClient

from src.app import create_app

client = TestClient(create_app())


def test_cors_headers():
    """Test that CORS headers are set correctly."""
    response = client.options("/", headers={"Origin": "http://localhost:8080"})

    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:8080"


def test_within_body_size():
    """Test that a request with a body within the size limit is accepted."""
    within_limit = b"a" * (1 * 1024 * 1024)
    response = client.post("/", content=within_limit)

    assert response.status_code != 413


def test_exceed_body_size():
    """Test that a request with a body exceeding the size limit is rejected."""
    exceed_limit = b"a" * (11 * 1024 * 1024)  # 11 MB
    response = client.post("/", content=exceed_limit)

    assert response.status_code == 413
    assert response.text == "Payload too large"
