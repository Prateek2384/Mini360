import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env.test")

test_url = os.environ.get("TEST_DATABASE_URL")
if not test_url:
    raise RuntimeError("TEST_DATABASE_URL is not set (see backend/.env.test)")
if "test" not in test_url.rsplit("/", 1)[-1]:
    raise RuntimeError("TEST_DATABASE_URL must point to a database whose name contains 'test'")

os.environ["DATABASE_URL"] = test_url
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ["COOKIE_SECURE"] = "false"

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(cfg, "head")


@pytest.fixture(autouse=True)
def clean_db():
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} CASCADE"))
    yield


@pytest.fixture
def make_client():
    clients = []

    def _make() -> TestClient:
        client = TestClient(app)
        clients.append(client)
        return client

    yield _make
    for client in clients:
        client.close()
