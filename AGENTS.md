# AGENTS.md

## What this repo is

FastAPI SaaS skeleton — auth, user management, multi-tenancy. Backend-only (no frontend). Designed to be copied per-project and built on top of.

## Setup

```bash
cd saas-template
uv sync                    # install all deps (including dev)
cp .env.example .env       # create local env (edit JWT_SECRET_KEY for real use)
uv run uvicorn app.main:app --reload   # start dev server
```

## Commands (exact order)

```bash
uv run ruff check .        # lint — must pass before commit
uv run mypy .              # typecheck — strict mode enabled
uv run pytest -x           # test — stops on first failure
```

## Architecture

Layered: **Routers → Services → Models → Database**

- `app/routers/` — HTTP endpoints only. No business logic here.
- `app/services/` — Business logic. Routers call services.
- `app/models/` — SQLAlchemy 2.0 async models. UUID PKs.
- `app/schemas/` — Pydantic v2 request/response validation.
- `app/config.py` — pydantic-settings, loads `.env`.
- `app/database.py` — async engine + session factory. `get_db` yields sessions.
- `app/dependencies.py` — `get_current_user` extracts JWT from header.

## Conventions

- Python 3.11+. Use `X | Y` union syntax, not `Optional[X]`.
- All DB operations async (`AsyncSession`, `select`, `await session.execute()`).
- mypy strict mode: must pass with zero errors.
- Ruff rules: E, F, I, N, UP, B, SIM. No manual formatting — let Ruff handle it.
- UUIDs for all primary keys (use `uuid.uuid4`).
- SQLite for dev (`dev.db`), Postgres for prod. Never commit `dev.db`.

## Multi-tenancy pattern

Shared DB + `org_id` foreign key. Three tables: `users`, `organizations`, `memberships`. The `role` field on memberships is an enum: owner, admin, member. Projects that don't need orgs simply skip those tables.

## Key files

- `doc/analysis.md` — Architecture diagrams, decisions log, Phase 1 checklist (20 items with exact function signatures).
- `pyproject.toml` — All deps + tool config (ruff, mypy, pytest).
- `.env.example` — Required env vars. Copy to `.env`.

## Gotchas

- `alembic/env.py` must import all models for `--autogenerate` to work.
- JWT tokens have no server-side revocation. Token expiry is configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`.
- `asyncpg` is the Postgres driver. `aiosqlite` is the SQLite driver. Both are async. Don't mix sync drivers.
- CORS is configurable via `CORS_ORIGINS` in `.env` (comma-separated, defaults to `*`). Lock down before deploying.
