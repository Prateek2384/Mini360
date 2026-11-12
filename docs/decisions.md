# Decisions log

| # | Area | Decision | Reason | Trade-off |
|---|---|---|---|---|
| 1 | Data | UUID primary keys | Harder to guess IDs in URLs | Longer IDs, harder to read while debugging |
| 2 | Data | Status columns as `VARCHAR` + `CHECK`, not PostgreSQL `ENUM` | Adding a value later is a simple migration | Allowed values are defined in two places (model and constraint) |
| 3 | Data | Questions copied into each assessment | Editing the question bank never changes past results | 10 extra rows per assessment; the app must check that answers belong to the same assessment |
| 4 | Lifecycle | `closes_at` (scheduled) + `closed_at` (actual); "lazy close" when an assessment or invitation is read | No background worker needed (PRD allows synchronous) | Status changes only when someone reads it |
| 5 | Privacy | `min_responses >= 3` enforced in the database as well as in code | A bug cannot lower the anonymity threshold | — |
| 6 | Privacy | Guest comments are not collected | PRD: comments must not be shown in the MVP; data not stored cannot leak | Less qualitative feedback |
| 7 | Privacy | Results and PDF share one gate (`build_results`) | The PDF cannot bypass the threshold | — |
| 8 | Security | Invitation token: 256-bit random, stored as SHA-256 hash | High-entropy tokens do not need a slow hash, and the hash allows lookup | Links are shown only once |
| 9 | Security | Session = signed HTTP-only cookie (`itsdangerous`), 7 days | No session table needed | Logout cannot invalidate a copied cookie |
| 10 | Security | Another leader's assessment returns 404, not 403 | Does not reveal that the ID exists | — |
| 11 | Security | Logs record route templates; uvicorn access log disabled in containers | Invitation tokens never appear in logs | Less detail in logs |
| 12 | API | Validation errors return 400 with a consistent `{"error": ...}` body | PRD lists 400/401/403/404/409 | Swagger still documents FastAPI's default 422 |
| 13 | API | Expired or closed invitations return 410 | Distinguishes "gone" from "already used" (409) | Not in the PRD's list of codes |
| 14 | Scoring | Full precision stored and returned; rounding to 1 decimal only in UI and PDF; focus-area ties broken by question order | PRD: round only for display; deterministic results | — |
| 15 | Report | PDF suggests the two lowest-rated categories; API keeps item-level focus areas (FR-07) | Simpler message for the leader | PDF and dashboard show slightly different levels of detail |
| 16 | Goals | `PUT /goals` replaces the whole list (1–2 goals) | Simple and idempotent | Goal IDs change on every save |
| 17 | Tooling | psycopg 3, system Python 3.12 virtualenv, Ruff, ESLint | Current, maintained tools; matches the Docker image | — |
| 18 | Local dev | Backend on port 8001 | Port 8000 was taken by another service on the dev machine | Must be documented for other developers |
| 19 | Deployment | One service: API mounted at `/api`, SPA at `/` | First-party cookies, no cross-site CORS/SameSite issues | Frontend and backend deploy together |
| 20 | Deployment | Render (Docker web service + managed PostgreSQL), auto-deploy on `main` | Runs the same Dockerfile; CD with little setup | Free plan sleeps when idle |
| 21 | Testing | Separate `*_test` database; tables truncated before every test | Tests never touch real data and do not depend on each other | Needs a running PostgreSQL |
| 22 | Testing | Playwright happy path runs locally, not in CI | PRD's CI list does not include e2e; needs the full stack | E2E regressions are caught only when run locally |
