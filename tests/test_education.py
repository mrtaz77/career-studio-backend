from fastapi.testclient import TestClient
from test_util import api_prefix, get_firebase_token

from src.app import create_app


def test_education_crud_flow():
    app = create_app()
    with TestClient(app) as client:
        # === Setup ===
        token = get_firebase_token()
        headers = {"Authorization": f"Bearer {token}"}

        # === Step 1: GET all entries ===
        get_resp = client.get(f"{api_prefix}/education", headers=headers)
        print(f"GET /education response: {get_resp.json()}")
        assert get_resp.status_code == 200
        original_entries = get_resp.json()
        assert isinstance(original_entries, list)

        if not original_entries:
            raise AssertionError("No education entries exist to begin test")

        # Work with the first education entry
        original = original_entries[0]
        education_id = original["id"]

        # === Step 2: DELETE the first education entry ===
        delete_resp = client.delete(
            f"{api_prefix}/education/{education_id}", headers=headers
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["message"] == "Education entry deleted"

        # === Step 3: ADD it back ===
        add_payload = [
            {
                "degree": original["degree"],
                "institution": original["institution"],
                "location": original["location"],
                "start_date": original["start_date"],
                "end_date": original["end_date"],
                "gpa": original["gpa"],
                "honors": original["honors"],
            }
        ]
        add_resp = client.post(
            f"{api_prefix}/education/add", json=add_payload, headers=headers
        )
        assert add_resp.status_code == 201
        assert add_resp.json()["message"] == "Education added"

        # === Step 4: GET again to find new education_id ===
        get_resp_2 = client.get(f"{api_prefix}/education", headers=headers)
        assert get_resp_2.status_code == 200
        new_entries = get_resp_2.json()

        # Assume last one is just added
        added = new_entries[-1]
        new_education_id = added["id"]

        # === Step 5: UPDATE (e.g., change degree) ===
        updated_degree = "Test Degree"
        patch_payload = {"degree": updated_degree}
        patch_resp = client.patch(
            f"{api_prefix}/education/{new_education_id}",
            json=patch_payload,
            headers=headers,
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["degree"] == updated_degree

        # === Step 6: REVERT back to original ===
        revert_payload = {"degree": original["degree"]}
        revert_resp = client.patch(
            f"{api_prefix}/education/{new_education_id}",
            json=revert_payload,
            headers=headers,
        )
        assert revert_resp.status_code == 200
        assert revert_resp.json()["degree"] == original["degree"]
