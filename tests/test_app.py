import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def activity_signup_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


@pytest.fixture(autouse=True)
def reset_activity_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    response = client.post(activity_signup_path(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_registration():
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    response = client.post(activity_signup_path(activity_name), params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_delete_removes_participant():
    activity_name = "Programming Class"
    email = "newstudent@mergington.edu"

    signup_response = client.post(activity_signup_path(activity_name), params={"email": email})
    assert signup_response.status_code == 200

    delete_response = client.delete(activity_signup_path(activity_name), params={"email": email})

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_404():
    activity_name = "Gym Class"
    email = "missingstudent@mergington.edu"

    response = client.delete(activity_signup_path(activity_name), params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up"
