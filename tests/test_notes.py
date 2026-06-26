import pytest
from httpx import AsyncClient


@pytest.fixture
async def owner_token(client: AsyncClient) -> str:
    response = await client.post(
        "/signup",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    return str(response.json()["access_token"])


@pytest.fixture
async def org_id(client: AsyncClient, owner_token: str) -> str:
    response = await client.post(
        "/organizations",
        json={"name": "Test Org", "slug": "test-org"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    return str(response.json()["id"])


@pytest.fixture
async def member_setup(client: AsyncClient, owner_token: str, org_id: str) -> str:
    resp = await client.post(
        "/signup",
        json={"email": "member@example.com", "password": "secret123"},
    )
    member_tok = str(resp.json()["access_token"])
    await client.post(
        f"/organizations/{org_id}/members",
        json={"email": "member@example.com", "role": "member"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    return member_tok


@pytest.mark.asyncio
async def test_create_note_returns_201(
    client: AsyncClient, owner_token: str, org_id: str
) -> None:
    response = await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "My Note", "body": "Hello world"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Note"
    assert data["body"] == "Hello world"
    assert data["org_id"] == org_id


@pytest.mark.asyncio
async def test_list_notes_returns_all(
    client: AsyncClient, owner_token: str, org_id: str
) -> None:
    await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "Note A", "body": ""},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "Note B", "body": ""},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    response = await client.get(
        f"/organizations/{org_id}/notes",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_note_returns_note(
    client: AsyncClient, owner_token: str, org_id: str
) -> None:
    create_resp = await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "Specific Note", "body": "content"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    note_id = create_resp.json()["id"]
    response = await client.get(
        f"/organizations/{org_id}/notes/{note_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Note"


@pytest.mark.asyncio
async def test_update_note_author_can_update(
    client: AsyncClient, owner_token: str, org_id: str
) -> None:
    create_resp = await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "Original", "body": "original"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    note_id = create_resp.json()["id"]
    response = await client.patch(
        f"/organizations/{org_id}/notes/{note_id}",
        json={"title": "Updated", "body": "updated"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["body"] == "updated"


@pytest.mark.asyncio
async def test_update_note_non_author_member_cannot_update(
    client: AsyncClient, owner_token: str, org_id: str, member_setup: str,
) -> None:
    create_resp = await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "Owner Note", "body": "private"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    note_id = create_resp.json()["id"]
    response = await client.patch(
        f"/organizations/{org_id}/notes/{note_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {member_setup}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_note_returns_204(
    client: AsyncClient, owner_token: str, org_id: str
) -> None:
    create_resp = await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "Delete Me", "body": ""},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    note_id = create_resp.json()["id"]
    response = await client.delete(
        f"/organizations/{org_id}/notes/{note_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 204
