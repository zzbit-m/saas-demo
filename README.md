# saas-template

Reusable FastAPI SaaS skeleton. Backend-only, no frontend. Covers auth, user management, and flexible multi-tenancy.

Copy this folder per-project, rename it, and start building features on top.

## Quick Start

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to test the API.

## What's Inside

| Feature | Status |
|---------|--------|
| Signup / Login (JWT) | Done |
| User model (UUID, email, password) | Done |
| Multi-tenancy (organizations + memberships) | Done |
| Role enum (owner, admin, member) | Done |
| Alembic migrations (async) | Done |
| CORS (configurable from `.env`) | Done |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/signup` | No | Create account, get JWT |
| POST | `/login` | No | Verify credentials, get JWT |
| GET | `/me` | Yes | Get current user |
| PATCH | `/me` | Yes | Update current user |
| GET | `/health` | No | Server health check |

## Configuration

Copy `.env.example` to `.env` and edit:

```bash
DATABASE_URL=sqlite+aiosqlite:///./dev.db   # dev
JWT_SECRET_KEY=your-secret-here              # change for prod
CORS_ORIGINS=*                               # comma-separated for prod
```

## Development

```bash
uv run ruff check .        # lint
uv run mypy .              # typecheck
uv run pytest -x           # test

uv run alembic revision --autogenerate -m "description"  # new migration
uv run alembic upgrade head                              # apply migrations
```

## Project Structure

```
app/
├── main.py           # FastAPI app, CORS, routers
├── config.py         # Settings from .env
├── database.py       # Async SQLAlchemy engine + session
├── dependencies.py   # get_current_user (JWT extraction)
├── models/           # SQLAlchemy models (User, Organization, Membership)
├── routers/          # API endpoints (auth, users)
├── schemas/          # Pydantic request/response validation
└── services/         # Business logic (password hashing, JWT, CRUD)
```

## Architecture

See `doc/analysis.md` for full architecture diagrams, decisions log, and status checklist.
