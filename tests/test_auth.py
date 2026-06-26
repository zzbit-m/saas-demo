import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/signup",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post(
        "/signup",
        json={"email": "test2@example.com", "password": "secret123"},
    )
    response = await client.post(
        "/login",
        json={"email": "test2@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
