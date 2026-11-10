from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
EXISTING_EMAIL = "existing@mergington.edu"
NEW_EMAIL = "new@mergington.edu"
TEST_ACTIVITIES = {
    ACTIVITY_NAME: {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": [EXISTING_EMAIL],
    }
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(TEST_ACTIVITIES))
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == TEST_ACTIVITIES


def test_signup_adds_participant(client):
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {NEW_EMAIL} for {ACTIVITY_NAME}"
    }
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [
        EXISTING_EMAIL,
        NEW_EMAIL,
    ]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_participant(client):
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": EXISTING_EMAIL},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]


def test_delete_removes_participant(client):
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": EXISTING_EMAIL},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {EXISTING_EMAIL} from {ACTIVITY_NAME}"
    }
    assert app_module.activities[ACTIVITY_NAME]["participants"] == []


def test_delete_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": EXISTING_EMAIL},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_delete_returns_404_for_unregistered_participant(client):
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]