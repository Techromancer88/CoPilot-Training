import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def activity_name(monkeypatch):
    name = "Test Club"
    monkeypatch.setitem(
        activities,
        name,
        {
            "description": "A test activity",
            "schedule": "Fridays",
            "max_participants": 5,
            "participants": [],
        },
    )
    return name


def test_get_activities_returns_available_activities(client, activity_name):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()
    assert response.headers["Cache-Control"] == "no-store"


def test_signup_adds_student_to_activity(client, activity_name):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_registration(client, activity_name):
    # Arrange
    email = "student@example.com"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    # Arrange

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup", params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404


def test_unregister_removes_student_from_activity(client, activity_name):
    # Arrange
    email = "student@example.com"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_student_not_signed_up(client, activity_name):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404


def test_unregister_rejects_unknown_activity(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup", params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404