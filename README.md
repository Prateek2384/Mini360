# Mini 360

A small 360-degree leadership feedback app (learning project).

## Stack
- Backend: FastAPI (Python 3.12+)
- Frontend: React + Vite + TypeScript
- Database: PostgreSQL 17 (Docker Compose)

## Local setup

### 1. Database
```
cp .env.example .env        # fill in the values
docker compose up -d
docker compose ps           # mini360-db should be (healthy)
```

### 2. Backend
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in DATABASE_URL
uvicorn app.main:app --reload --port 8001
```
- Health check: http://127.0.0.1:8001/health
- API docs: http://127.0.0.1:8001/docs

### 3. Frontend
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Environment variables

| File | Variable | Purpose |
|---|---|---|
| `.env` | `POSTGRES_USER` | Database user created on first start |
| `.env` | `POSTGRES_PASSWORD` | Password for that user |
| `.env` | `POSTGRES_DB` | Database name |
| `backend/.env` | `DATABASE_URL` | Connection string used by FastAPI |

Note: the database password is only applied the first time the
Postgres volume is created. Changing `.env` later does not change it.

## Documentation

- [ER diagram and database rules](docs/er-diagram.md)
- [Decisions log](docs/decisions.md)
- [Testing and evidence](docs/testing.md)
- [Design notes, wireframes and iterations](docs/design.md)
- [Retrospective](docs/retrospective.md)
