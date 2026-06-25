# saas-template

FastAPI SaaS backend skeleton — auth, multi-tenancy, JWT. Copy and build on top of.

## What's included

- Auth: signup, login, refresh token
- JWT access + refresh tokens
- User model (UUID PK, email, password hash)
- Organization + membership multi-tenancy (roles: owner, admin, member)
- Alembic migrations (async)
- Async SQLAlchemy 2.0
- uv toolchain: ruff (lint), mypy (typecheck), pytest (test)

## What's not included

- Frontend
- Billing (Stripe)
- Real-time (WebSockets)
- OAuth (Google/GitHub)

Add these per project as needed.

## Quick start

```bash
uv sync
cp .env.example .env
alembic upgrade head
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to test the API.

## Commands

```bash
uv run ruff check .        # lint
uv run mypy .              # typecheck
uv run pytest -x           # test
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/signup` | No | Create account, get tokens |
| POST | `/login` | No | Verify credentials, get tokens |
| POST | `/refresh` | No | Get new tokens from refresh token |
| GET | `/users/me` | Yes | Get current user |
| PATCH | `/users/me` | Yes | Update current user |
| GET | `/health` | No | Server health check |
