import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.environ["FIREBASE_API_KEY"]
USER_EMAIL = os.environ["USER_1_EMAIL"]
USER_PASSWORD = os.environ["USER_1_PASSWORD"]


def fetch_firebase_token(email: str, password: str) -> str:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }

    response = httpx.post(url, json=payload)
    response.raise_for_status()
    return response.json()["idToken"]


def setup_firebase_tokens():
    token = fetch_firebase_token(USER_EMAIL, USER_PASSWORD)
    setup_data = {"USER_1_TOKEN": token}

    setup_path = Path(__file__).parent / "setup_data.json"
    setup_path.write_text(json.dumps(setup_data))
    print("Firebase token saved to setup_data.json")


if __name__ == "__main__":
    setup_firebase_tokens()
