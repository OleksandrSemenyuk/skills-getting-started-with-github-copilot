import asyncio
import copy

import httpx
import pytest

from src import app as app_module


def perform_request(app, method, url, **kwargs):
    async def _request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, url, **kwargs)

    return asyncio.run(_request())


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_state = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_data():
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = perform_request(app_module.app, "GET", "/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity_name in data
    assert data[expected_activity_name]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = perform_request(
        app_module.app,
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    perform_request(
        app_module.app,
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = perform_request(
        app_module.app,
        "DELETE",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert f"Removed {email}" in response.json()["message"]
    assert email not in app_module.activities[activity_name]["participants"]
