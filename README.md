# saas-demo

Multi-tenant team notes app built on [saas-template](https://github.com/zzbit-m/saas-template).

Shows the full pattern: signup → create org → invite members → collaborate on notes.

## Try it live

- **Frontend**: [https://saas-demo-bay.vercel.app](https://saas-demo-bay.vercel.app)
- **API docs**: (deploy backend first — see below)

## Quick start (backend only)

```bash
uv sync --all-extras
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to explore the API.

## Quick start (full stack)

```bash
docker compose up --build
```

Open http://localhost to use the web UI.

## Quick start (frontend dev mode)

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`. Start both the backend (`uv run uvicorn ...`) and the frontend dev server.

## Tutorial

See [docs/tutorial.md](docs/tutorial.md) for a step-by-step walkthrough using curl commands.

## Endpoints

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/signup` | No | Create account, get tokens |
| POST | `/login` | No | Verify credentials, get tokens |
| POST | `/refresh` | No | Get new tokens from refresh token |

### Users
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/users/me` | Yes | Get current user |
| PATCH | `/users/me` | Yes | Update current user |

### Organizations
| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/organizations` | Yes | — | Create org (you become owner) |
| GET | `/organizations` | Yes | — | List my orgs |
| GET | `/organizations/{id}` | Yes | member | Get org details |
| PATCH | `/organizations/{id}` | Yes | owner/admin | Update org |
| GET | `/organizations/{id}/members` | Yes | member | List members |
| POST | `/organizations/{id}/members` | Yes | owner/admin | Invite by email |
| DELETE | `/organizations/{id}/members/{uid}` | Yes | owner/admin | Remove member |

### Notes (org-scoped)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/organizations/{id}/notes` | Yes | List notes in org |
| POST | `/organizations/{id}/notes` | Yes | Create note |
| GET | `/organizations/{id}/notes/{nid}` | Yes | Get note |
| PATCH | `/organizations/{id}/notes/{nid}` | Yes | Update (author or admin) |
| DELETE | `/organizations/{id}/notes/{nid}` | Yes | Delete (author or admin) |

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Server health check |

## Commands

```bash
uv run ruff check .        # lint
uv run mypy .              # typecheck
uv run pytest -x           # test (17 tests)
```

## Architecture

Layered: **Routers → Services → Models → Database**
- No business logic in routers
- No HTTP in services
- UUID primary keys on all models
- Async SQLAlchemy 2.0 everywhere

## Deploy backend (Railway — free)

1. Go to [railway.com/new](https://railway.com/new)
2. Import `zzbit-m/saas-demo`
3. Add a **PostgreSQL** database (it auto-provisions)
4. Set environment variables:
   - `JWT_SECRET_KEY` → a random string
   - `CORS_ORIGINS` → `https://saas-demo-bay.vercel.app`
5. Deploy
6. Copy your Railway URL (e.g. `https://saas-demo.up.railway.app`)
7. In Vercel dashboard → your project → **Environment Variables** → add `VITE_API_BASE_URL` = `https://saas-demo.up.railway.app`
8. Redeploy the frontend

## Frontend

React + Vite + TypeScript + Tailwind CSS v4. Lives in `frontend/`.

- **Dev**: `cd frontend && npm install && npm run dev`
- **Build**: `cd frontend && npm run build` (outputs to `frontend/dist/`)
- **Docker**: `docker compose up --build` (Nginx serves the built app, proxies `/api` to the backend)
