# Mini 360

A small, privacy-first 360° leadership feedback app. A leader creates an assessment, rates themselves on 10 behaviours, invites at least three colleagues through one-time links (no account needed), and — once the survey closes — sees anonymous aggregate scores, self-vs-others gaps and suggested focus areas. They can record two development commitments and download a PDF summary.

> Learning project built against the *Mini 360° Leadership Assessment PRD v1.0*. Uses fictional data only.

## Live

| | URL |
|---|---|
| App | https://mini360.onrender.com |
| API docs (Swagger) | https://mini360.onrender.com/api/docs |
| Health check | https://mini360.onrender.com/api/health |

The free hosting plan sleeps after inactivity, so the first request can take up to about a minute.

## Features

- Email/password accounts (Argon2 hashing, HTTP-only session cookie)
- Assessments with a closing date; draft → open → closed (closed automatically once the date passes)
- 10 questions across Communication, Collaboration and Accountability, rated 1–5
- Self-assessment for the leader
- One-time, unguessable invitation links for raters (only a SHA-256 hash is stored)
- Results unlock only when the survey is **closed** and has **at least 3** rater responses
- Aggregate results only: item, category and overall means, self-vs-others gaps, focus areas
- Two development commitments with due dates and status
- PDF report with permitted aggregate data only

## Architecture

```mermaid
flowchart LR
  B[Browser] -->|HTTPS| S["Render web service<br/>(app.serve)"]
  S -->|"/ and /assets"| F[React SPA - built static files]
  S -->|"/api/*"| A["FastAPI API<br/>(app.main)"]
  A -->|SQLAlchemy + psycopg| D[(PostgreSQL 17)]
  G[GitHub] -->|pull request| C["GitHub Actions CI<br/>ruff, pytest, eslint, build"]
  G -->|merge to main| S
```

- **One service, one domain.** The production image serves the React app at `/` and mounts the API at `/api`, so the session cookie is first-party and no cross-site cookie or CORS setup is needed.
- **Local development** mirrors this: Vite proxies `/api/*` to the backend on `127.0.0.1:8001`.
- Migrations run automatically on container start (`alembic upgrade head`).

### Tech stack

| Layer | Choice |
|---|---|
| Frontend | React, Vite, TypeScript, Tailwind CSS, React Router |
| Backend | Python 3.12, FastAPI, Pydantic |
| Database | PostgreSQL 17, SQLAlchemy 2, Alembic |
| Auth | Argon2 (`argon2-cffi`), signed HTTP-only cookie (`itsdangerous`) |
| PDF | ReportLab |
| Tests | pytest, FastAPI TestClient, Playwright |
| CI/CD | GitHub Actions (CI), Render auto-deploy on `main` (CD) |
| Containers | Docker, Docker Compose |

## Repository layout

```
backend/
  app/
    core/       config, database, sessions, errors, logging, security
    models/     SQLAlchemy models (7 tables)
    schemas/    Pydantic request/response schemas
    routes/     API endpoints
    services/   business logic (scoring, privacy gate, PDF, ...)
    main.py     API app
    serve.py    production app: API at /api + SPA
  alembic/      migrations
  tests/        pytest suite
frontend/
  src/          React app
  e2e/          Playwright test
Dockerfile          production image (frontend + backend)
docker-compose.yml  local Postgres, API, and production-like "web" profile
```

## Local setup

**Prerequisites:** Docker with Compose, Python 3.12+, Node.js 24+, Git.

### 1. Clone

```bash
git clone <repo-url> mini-360-assessment
cd mini-360-assessment
```

### 2. Database

```bash
cp .env.example .env          # fill in POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
docker compose up -d db
docker compose ps             # mini360-db should show (healthy)
```

The password is applied only when the Postgres volume is first created. Changing `.env` later does not change it.

### 3. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in the values (see Environment variables)
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Check: `curl http://127.0.0.1:8001/health` → `{"status":"ok","database":"ok"}`. Local API docs: http://127.0.0.1:8001/docs

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api/*` to `127.0.0.1:8001`.

### Run with Docker instead

```bash
docker compose up -d --build                     # db + API on 127.0.0.1:8001
docker compose --profile prod up -d --build web  # production image on http://localhost:8080
```

Do not run the local `uvicorn` and the `api` container at the same time; both use port 8001.

## Environment variables

Real values live only in git-ignored `.env` files locally and in Render's environment settings in production. Never commit them.

| File / place | Variable | Purpose |
|---|---|---|
| `.env` (root) | `POSTGRES_USER` | Database user created on first start |
| `.env` (root) | `POSTGRES_PASSWORD` | Password for that user |
| `.env` (root) | `POSTGRES_DB` | Database name |
| `backend/.env` | `DATABASE_URL` | `postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/DBNAME` (`postgresql://` is also accepted) |
| `backend/.env` | `SECRET_KEY` | Signs session cookies. Generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `backend/.env` | `CORS_ORIGINS` | Allowed frontend origins, comma-separated |
| `backend/.env` | `FRONTEND_URL` | Base URL used in invitation links |
| `backend/.env` | `COOKIE_SECURE` | `false` locally, `true` in production (HTTPS) |
| `backend/.env.test` | `TEST_DATABASE_URL` | Separate test database; its name must contain `test` |
| `frontend` (optional) | `VITE_API_URL` | API base path, defaults to `/api` |
| Render | `PORT` | Set by Render automatically |

## Database migrations

```bash
cd backend && source venv/bin/activate
alembic upgrade head                                       # apply all migrations
alembic revision --autogenerate -m "describe the change"   # after changing a model; review the file before applying
```

In Docker and production, `alembic upgrade head` runs automatically before the server starts.

## Testing

**Backend (19 tests):** scoring, auth, privacy gate, ownership, one-time links, expiry.

```bash
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "CREATE DATABASE mini360_test;"
# backend/.env.test: TEST_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/mini360_test
cd backend && source venv/bin/activate
ruff check .
pytest -q
```

**Frontend-to-API happy path (Playwright):** needs the backend running on port 8001.

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

**CI:** every pull request and every push to `main` runs ruff, pytest (with a Postgres service), ESLint and the frontend build.

## Deployment (Render)

1. Create a **PostgreSQL 17** database and copy its **Internal Database URL**.
2. Create a **Web Service** from this repository, runtime **Docker**, Dockerfile `./Dockerfile`, same region as the database.
3. Set environment variables: `DATABASE_URL` (internal URL), a new `SECRET_KEY`, `COOKIE_SECURE=true`, and `CORS_ORIGINS` and `FRONTEND_URL` set to the service URL (no trailing slash).
4. Health check path: `/api/health`.
5. Auto-deploy on `main` is the CD step: merging a pull request builds the image, runs migrations and releases the new version.

## Rollback

1. Render dashboard → service → **Events** → choose the last good deploy → **Rollback**.
2. If the release you are rolling back included a **database migration**, rolling back the code alone is not enough. Check `alembic history`, take a database backup, and only then run `alembic downgrade -1` against the production database.
3. Alternatively, revert the commit on GitHub (`git revert`) and merge it; CD redeploys the previous behaviour.

## Privacy and security

- Passwords are hashed with Argon2; plain passwords are never stored or logged.
- Session cookie is HTTP-only, `SameSite=Lax`, and `Secure` in production.
- Invitation tokens are 256-bit random values; only their SHA-256 hash is stored, and each link submits once.
- Leaders can only access their own assessments; other IDs return 404.
- The results API and PDF return aggregates only, after closure and at least 3 rater responses. Guest comments are not collected.
- Logs record route templates (for example `/invitations/{token}`), never raw tokens; the server access log is disabled.

## Scoring

- Item: `others_mean` = average of rater scores (self excluded).
- Category: average of its item means. Overall: average of all 10 item means.
- Gap = self score − others mean (positive means the leader rated themselves higher).
- Focus areas: the two lowest-rated items (ties broken by question order). The PDF suggests the two lowest-rated categories. These are simple suggestions, not validated psychological findings.
- Values are stored at full precision and rounded to one decimal only for display.

## Known limitations

- Logout removes the cookie from the browser, but a copied cookie stays valid until it expires (7 days); server-side sessions would fix this.
- Invitation links are shown only once; there is no email delivery or reminder yet.
- Questions are copied into each assessment, so editing the question bank does not change existing assessments.
- No rate limiting on login.
- Validation errors return 400 (as per the PRD), but Swagger still documents 422.
- The free hosting plan sleeps when idle, causing a slow first request.
- The Playwright test runs locally, not in CI.
