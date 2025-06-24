import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_full_expected_workflow(client, mysql_container):
    # Register test user
    register_response = client.post("/api/register", json={
        "username": "e2euser",
        "password": "strongpass123"
    })
    assert register_response.status_code == 201

    # Login
    login_response = client.post("/api/token", data={
        "username": "e2euser",
        "password": "strongpass123"
    })
    assert login_response.status_code == 200

    # Instead of reading from JSON, read from cookies:
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None, "No access_token cookie set"

    # Use the access_token cookie in the Authorization header (if your API requires it)
    hs_response = client.post(
        "/api/highscore",
        json={"score": 1337},
        cookies={"access_token": access_token}
    )
    assert hs_response.status_code == 200
    result = hs_response.json()
    assert result[1] == "e2euser"
    assert result[2] == 1337

    # Request highscores, use auth token
    get_response = client.get(
        "/api/highscores",
        cookies={"access_token": access_token}
    )
    assert get_response.status_code == 200
    assert any(score["username"] == "e2euser" and score["score"]
               == 1337 for score in get_response.json())
