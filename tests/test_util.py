import json
from pathlib import Path

api_prefix = "/api/v1"


def get_firebase_token():
    path = Path(__file__).parent / "setup_data.json"
    with open(path) as f:
        return json.load(f)["USER_1_TOKEN"]
