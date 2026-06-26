# saas-demo Tutorial

This tutorial walks through building a multi-tenant team notes app using the FastAPI SaaS template. You'll see the full pattern: model → service → schema → router → test.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- This repo cloned and dependencies installed

```bash
uv sync --all-extras
cp .env.example .env
uv run alembic upgrade head
```

## Architecture Review

```
Startup: fastapi dev server
   │
   ▼
   Router (HTTP handling)
   │
   ▼
   Service (business logic)
   │
   ▼
   Model (SQLAlchemy DB access)
   │
   ▼
   Database (SQLite dev / Postgres prod)
```

No business logic in routers. No HTTP in services. This separation keeps everything testable.

## Step 1: Sign up two users

Open 3 terminals. In terminal 1, start the server:

```bash
uv run uvicorn app.main:app --reload
```

In terminal 2, create an owner user:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret123"}'
```

Save the `access_token` from the response. In terminal 3, create a second user:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@example.com", "password": "secret123"}'
```

## Step 2: Create an organization

```bash
curl -X POST http://127.0.0.1:8000/organizations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ALICE_TOKEN" \
  -d '{"name": "Acme Corp", "slug": "acme-corp"}'
```

Save the `id` from the response (this is the `org_id`).

## Step 3: Invite Bob

```bash
curl -X POST http://127.0.0.1:8000/organizations/ORG_ID/members \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ALICE_TOKEN" \
  -d '{"email": "bob@example.com", "role": "member"}'
```

## Step 4: Create and share notes (Alice)

```bash
# Create a note
curl -X POST http://127.0.0.1:8000/organizations/ORG_ID/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ALICE_TOKEN" \
  -d '{"title": "Q4 Planning", "body": "Review budget and timeline"}'

# Save the note_id from the response, then list all notes
curl http://127.0.0.1:8000/organizations/ORG_ID/notes \
  -H "Authorization: Bearer ALICE_TOKEN" \
  | python -m json.tool
```

## Step 5: Bob reads the note

```bash
curl http://127.0.0.1:8000/organizations/ORG_ID/notes/NOTE_ID \
  -H "Authorization: Bearer BOB_TOKEN"
```

Bob can read but cannot edit Alice's note:

```bash
curl -X PATCH http://127.0.0.1:8000/organizations/ORG_ID/notes/NOTE_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer BOB_TOKEN" \
  -d '{"title": "Hacked"}'
# Returns 403 Forbidden
```

Only the author or an admin can update/delete a note.

## How the Notes feature is built

### 1. Model (`app/models/note.py`)

SQLAlchemy model with FK to organizations and users, timestamp fields.

```python
class Note(Base):
    __tablename__ = "notes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=...)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

### 2. Schema (`app/schemas/note.py`)

Pydantic v2 models for request/response validation.

```python
class CreateNoteRequest(BaseModel):
    title: str
    body: str = ""

class NoteResponse(BaseModel):
    id: str
    org_id: str
    title: str
    body: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
```

### 3. Service (`app/services/note.py`)

Pure async functions — no HTTP logic, just DB operations.

```python
async def create_note(db, org_id, title, body, created_by) -> Note: ...
async def get_notes(db, org_id) -> list[Note]: ...
async def get_note(db, note_id) -> Note | None: ...
async def update_note(db, note, title, body) -> Note: ...
async def delete_note(db, note_id) -> bool: ...
```

### 4. Router (`app/routers/notes.py`)

Endpoints wrapped with `Depends(get_org_membership)` for authorization.

```python
@router.post("/organizations/{org_id}/notes", ...)
async def create_note_endpoint(
    body: CreateNoteRequest,
    # ^^^ validates request body
    membership: Membership = Depends(get_org_membership),
    # ^^^ checks user is member of org_id, returns their Membership
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    note = await create_note(db, membership.org_id, body.title, body.body, current_user.id)
    return NoteResponse.model_validate(note)
```

### 5. Test (`tests/test_notes.py`)

Integration tests using in-memory SQLite. Pattern: set up user + org + data, call endpoint, assert.

```python
async def test_create_note_returns_201(client, owner_token, org_id):
    response = await client.post(
        f"/organizations/{org_id}/notes",
        json={"title": "My Note", "body": "Hello world"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 201
```

### 6. Migration

```bash
uv run alembic revision --autogenerate -m "Add notes table"
uv run alembic upgrade head
```

## Adding your own feature

The pattern is always the same:

1. **Model** → Define the table
2. **Schema** → Define request/response shapes
3. **Service** → Write business logic (pure DB ops)
4. **Router** → Wire up HTTP endpoints with auth
5. **Migration** → Generate + apply
6. **Test** → Write integration tests
7. Run `uv run ruff check . && uv run mypy . && uv run pytest -x`

That's it. Each layer has one job. You can swap SQLite for Postgres by changing `DATABASE_URL` in `.env`.
