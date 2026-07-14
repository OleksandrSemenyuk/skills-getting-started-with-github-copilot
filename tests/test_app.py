import asyncio

import httpx

from src.app import app


def perform_request(method, url, **kwargs):
    async def _request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, url, **kwargs)

    return asyncio.run(_request())


def test_unregister_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    signup_response = perform_request(
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    unregister_response = perform_request(
        "DELETE",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert "Removed" in unregister_response.json()["message"]

    activities_response = perform_request("GET", "/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]
