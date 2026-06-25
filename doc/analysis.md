# SaaS Template — Architecture & Decisions

## Overview

Reusable FastAPI SaaS skeleton. Backend-only, no frontend. Covers auth, user management, and flexible multi-tenancy. Copy this folder per-project, rename, and start building features.

---

## Architecture Diagrams

### System Flow

```
Client (curl / your frontend)
    │
    │  HTTP request
    │
    ▼
┌─────────────────────────────────────┐
│           FastAPI App               │
│                                     │
│  ┌─────────┐    ┌──────────────┐   │
│  │ Routers │───▶│  Services    │   │
│  │ (auth,  │    │ (business    │   │
│  │  users) │    │  logic)      │   │
│  └─────────┘    └──────┬───────┘   │
│       │                │           │
│       ▼                ▼           │
│  ┌─────────────────────────────┐   │
│  │      SQLAlchemy Models      │   │
│  │   (User, Org, Membership)   │   │
│  └─────────────┬───────────────┘   │
│                │                   │
│  ┌─────────────▼───────────────┐   │
│  │    Alembic Migrations       │   │
│  └─────────────┬───────────────┘   │
└────────────────┼───────────────────┘
                 │
                 ▼
           ┌──────────┐
           │ Postgres │
           └──────────┘
```

### Architecture Layers

```
┌──────────────────────────────────────┐
│        API Layer (Routers)           │  HTTP request/response
├──────────────────────────────────────┤
│       Service Layer (Business)       │  Logic, validation, orchestration
├──────────────────────────────────────┤
│       Data Layer (SQLAlchemy)        │  Models, queries, relationships
├──────────────────────────────────────┤
│       Config Layer (pydantic-settings)│  .env, DB URLs, secrets
└──────────────────────────────────────┘
```

### ER Diagram

```
┌──────────────┐       ┌──────────────┐
│ organizations│       │    users     │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ name         │       │ email        │
│ slug         │       │ hashed_password  │
│ created_at   │       │ is_active    │
└──────┬───────┘       │ created_at   │
       │               └──────┬───────┘
       │                      │
       │   ┌──────────────────┘
       │   │
  ┌────▼───▼──────┐
  │  memberships   │
  ├───────────────┤
  │ id (PK)       │
  │ user_id (FK)  │
  │ org_id (FK)   │
  │ role          │  "owner", "admin", "member"
  │ created_at    │
  └───────────────┘
```

---

## File Structure

```
saas-template/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, middleware, router includes
│   ├── config.py               # pydantic-settings: env vars, typed config
│   ├── database.py             # SQLAlchemy engine, session, Base
│   ├── dependencies.py         # get_db, get_current_user
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── organization.py     # Organization model
│   │   └── membership.py       # Membership model (user ↔ org)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # POST /signup, POST /login
│   │   └── users.py            # GET /me, PATCH /me
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # SignupRequest, LoginRequest, TokenResponse
│   │   └── user.py             # UserResponse, UserUpdate
│   └── services/
│       ├── __init__.py
│       ├── auth.py             # password hashing, JWT create/verify
│       └── user.py             # user CRUD
├── alembic/
│   ├── env.py                  # Alembic config, async engine, model imports
│   ├── script.py.mako          # Migration file template
│   └── versions/               # Migration files (auto-generated)
├── doc/
│   └── analysis.md             # Architecture, decisions, status checklist
├── alembic.ini                 # Alembic settings
├── pyproject.toml              # Dependencies + tool config
├── uv.lock                     # Lockfile (commit this)
├── .env.example                # Env var template — copy to .env
├── .gitignore
├── AGENTS.md                   # OpenCode session instructions
└── README.md                   # Project overview + setup
```

---

## Decisions Log

### 1. FastAPI (over Django, Express)

| Option | Pros | Cons |
|--------|------|------|
| **FastAPI** (chosen) | Async, auto-docs, type-safe, lightweight | Smaller ecosystem than Django |
| Django | Batteries-included, admin panel | Heavy, opinionated, REST framework is separate |
| Express (Node) | Huge ecosystem, same language as JS frontends | No type safety by default, ORM options weaker |

**Decision**: FastAPI — best fit for a lightweight, reusable API skeleton.

### 2. SQLAlchemy 2.0 (over Tortoise, Prisma)

| Option | Pros | Cons |
|--------|------|------|
| **SQLAlchemy 2.0** (chosen) | Mature, flexible, async support, huge community | More boilerplate than Prisma |
| Tortoise ORM | Django-like syntax, async native | Smaller community, less mature |
| Prisma | Type-safe, auto-generated client | Python support is newer, less flexible |

**Decision**: SQLAlchemy — most battle-tested Python ORM, pairs perfectly with FastAPI.

### 3. Shared-DB Multi-tenancy (over schema-per-tenant, DB-per-tenant)

| Option | Pros | Cons |
|--------|------|------|
| **Shared DB + org_id** (chosen) | Simple, cheap, works for most SaaS | Harder to enforce strict isolation |
| Schema-per-tenant | Stronger isolation | Migration complexity, more overhead |
| DB-per-tenant | Maximum isolation | Expensive, operational burden |

**Decision**: Shared DB — covers 90% of SaaS needs. Projects needing strict isolation can migrate later.

### 4. JWT (over session-based auth)

| Option | Pros | Cons |
|--------|------|------|
| **JWT** (chosen) | Stateless, scalable, works across services | No server-side revocation without extra infra |
| Sessions | Server-side revocation, simpler | Needs session store (Redis), harder to scale |

**Decision**: JWT — standard for APIs, stateless, works well for the template scope.

### 5. PostgreSQL + SQLite

| Option | Pros | Cons |
|--------|------|------|
| **Postgres** (prod) | JSONB, row-level security, mature | Needs server |
| **SQLite** (dev) | Zero config, single file | No advanced features, single-writer |

**Decision**: SQLite for dev (zero friction), Postgres for production (standard SaaS DB).

---

## Status Checklist

### Phase 1: Core Auth + User Management (detailed)

- [x] `app/config.py` — Settings class loads from `.env`, exposes `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` — **Settings class at line 4, all 4 fields present** (`app/config.py:4-15`)
- [x] `app/database.py` — Async SQLAlchemy engine created from `settings.DATABASE_URL`, `async_sessionmaker` session factory, `Base` declarative base, `get_db` async generator yields sessions — **All 4 components** (`app/database.py:8-19`)
- [x] `app/models/user.py` — `User` model with `id` (UUID PK), `email` (unique, indexed), `hashed_password`, `is_active` (bool), `created_at` (datetime) — **All 5 fields, UUID PK via uuid4** (`app/models/user.py:10-19`)
- [x] `app/models/organization.py` — `Organization` model with `id` (UUID PK), `name`, `slug` (unique), `created_at` — **All 4 fields** (`app/models/organization.py:10-18`)
- [x] `app/models/membership.py` — `Membership` model with `id` (UUID PK), `user_id` (FK → users), `org_id` (FK → organizations), `role` (enum: owner/admin/member), `created_at` — **SQLAlchemy Enum type, enforced at DB level** (`app/models/membership.py:9,18`)
- [x] `app/services/auth.py` — `hash_password(password) → str`, `verify_password(plain, hashed) → bool`, `create_access_token(user_id) → str`, `decode_access_token(token) → user_id` — **All 4 functions** (`app/services/auth.py:11-39`)
- [x] `app/schemas/auth.py` — `SignupRequest` (email, password), `LoginRequest` (email, password), `TokenResponse` (access_token, token_type) — **All 3 schemas** (`app/schemas/auth.py:4-16`)
- [x] `app/schemas/user.py` — `UserResponse` (id, email, is_active, created_at), `UserUpdate` (email optional) — **Both schemas, email is `EmailStr | None = None`** (`app/schemas/user.py:6-16`)
- [x] `app/routers/auth.py` — `POST /signup` creates user + returns token, `POST /login` verifies credentials + returns token — **409 on duplicate email, 401 on bad credentials** (`app/routers/auth.py:12-44`)
- [x] `app/routers/users.py` — `GET /me` returns current user, `PATCH /me` updates current user — **Both endpoints** (`app/routers/users.py:13-25`)
- [x] `app/dependencies.py` — `get_current_user` dependency extracts JWT from Authorization header, returns User — **OAuth2PasswordBearer + decode + fetch, 401 on invalid/missing** (`app/dependencies.py:13-31`)
- [x] `app/main.py` — FastAPI app created, routers included, CORS middleware added (configurable origins) — **`CORS_ORIGINS` read from `.env`, defaults to `"*"`** (`app/main.py:9-15`, `app/config.py:17`)
- [x] `alembic/env.py` — Alembic configured to use async engine, imports all models for autogenerate — **async_engine_from_config + all 3 models imported** (`alembic/env.py:1-61`)
- [x] `alembic.ini` — Points to correct `sqlalchemy.url` (reads from env) — **`sqlalchemy.url = sqlite+aiosqlite:///./dev.db`** (`alembic.ini:4`)
- [x] `alembic/versions/` — Initial migration generated for User, Organization, Membership tables — **Migration `86a0efa5085b` generated and applied** (`alembic/versions/86a0efa5085b_initial.py`)
- [x] `.env.example` — Contains all required env vars with placeholder values — **All 6 vars present** (`.env.example:1-16`)
- [x] `pyproject.toml` — All dependencies listed, dev dependencies (pytest, ruff, mypy) included — **11 deps + 6 dev deps** (`pyproject.toml:6-30`)
- [x] Project runs: `uv sync && uv run uvicorn app.main:app` starts without errors — **Verified: `/health` returns 200**
- [x] Project lints: `uv run ruff check .` passes with no errors — **Verified: "All checks passed!"**
- [x] Project typechecks: `uv run mypy .` passes with no errors — **Verified: "Success: no issues found in 19 source files"**

### Future phases (named only)

- **Phase 2: Email verification + password reset** — Confirm signup emails, forgot-password flow
- **Phase 3: OAuth login** — Google/GitHub OAuth via Authlib or similar
- **Phase 4: Role-based access control** — Enforce permissions per role (owner/admin/member) on endpoints
- **Phase 5: Rate limiting + security hardening** — CORS lockdown, rate limits, input sanitization
- **Phase 6: Docker + deployment** — Dockerfile, docker-compose, CI/CD pipeline
- **Phase 7: Testing** — Unit tests for services, integration tests for routers, test fixtures
