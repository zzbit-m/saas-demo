import pytest
from httpx import AsyncClient


@pytest.fixture
async def token(client: AsyncClient) -> str:
    response = await client.post(
        "/signup",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    return str(response.json()["access_token"])


@pytest.fixture
async def org_id(client: AsyncClient, token: str) -> str:
    response = await client.post(
        "/organizations",
        json={"name": "Test Org", "slug": "test-org"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return str(response.json()["id"])


@pytest.mark.asyncio
async def test_create_org_returns_201(client: AsyncClient, token: str) -> None:
    response = await client.post(
        "/organizations",
        json={"name": "My Org", "slug": "my-org"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Org"
    assert data["slug"] == "my-org"
    assert data["role"] == "owner"


@pytest.mark.asyncio
async def test_create_org_duplicate_slug_returns_409(
    client: AsyncClient, token: str, org_id: str
) -> None:
    response = await client.post(
        "/organizations",
        json={"name": "Another Org", "slug": "test-org"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_org_unauthenticated_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/organizations",
        json={"name": "Bad Org", "slug": "bad-org"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_orgs_returns_user_orgs(
    client: AsyncClient, token: str, org_id: str
) -> None:
    response = await client.get(
        "/organizations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert any(o["id"] == org_id for o in data)


@pytest.mark.asyncio
async def test_get_org_returns_org(
    client: AsyncClient, token: str, org_id: str
) -> None:
    response = await client.get(
        f"/organizations/{org_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == "Test Org"
    assert data["role"] == "owner"


@pytest.mark.asyncio
async def test_get_org_non_member_returns_403(
    client: AsyncClient, org_id: str
) -> None:
    other_token = (await client.post(
        "/signup",
        json={"email": "intruder@example.com", "password": "secret123"},
    )).json()["access_token"]
    response = await client.get(
        f"/organizations/{org_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invite_member_returns_201(
    client: AsyncClient, token: str, org_id: str
) -> None:
    await client.post(
        "/signup",
        json={"email": "member@example.com", "password": "secret123"},
    )
    response = await client.post(
        f"/organizations/{org_id}/members",
        json={"email": "member@example.com", "role": "member"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "member@example.com"
    assert data["role"] == "member"


@pytest.mark.asyncio
async def test_invite_member_non_admin_returns_403(
    client: AsyncClient, token: str, org_id: str
) -> None:
    member_token = (await client.post(
        "/signup",
        json={"email": "regular@example.com", "password": "secret123"},
    )).json()["access_token"]
    await client.post(
        f"/organizations/{org_id}/members",
        json={"email": "regular@example.com", "role": "member"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.post(
        f"/organizations/{org_id}/members",
        json={"email": "nobody@example.com", "role": "member"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_members_returns_all(
    client: AsyncClient, token: str, org_id: str
) -> None:
    await client.post(
        "/signup",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    await client.post(
        f"/organizations/{org_id}/members",
        json={"email": "alice@example.com", "role": "member"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        f"/organizations/{org_id}/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    emails = [m["email"] for m in data]
    assert "owner@example.com" in emails
    assert "alice@example.com" in emails
