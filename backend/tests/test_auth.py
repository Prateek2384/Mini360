from sqlalchemy import text

from app.core.database import engine
from tests.helpers import PASSWORD, register_and_login


def test_register_hashes_password_and_never_returns_it(make_client):
    c = make_client()
    r = c.post("/auth/register", json={"name": "Rahul", "email": "Rahul@Example.com", "password": PASSWORD})
    assert r.status_code == 201
    assert r.json()["email"] == "rahul@example.com"
    assert "password" not in r.text
    with engine.connect() as conn:
        stored = conn.execute(
            text("SELECT password_hash FROM users WHERE email = 'rahul@example.com'")
        ).scalar_one()
    assert stored.startswith("$argon2id$")
    assert PASSWORD not in stored


def test_duplicate_email_is_rejected(make_client):
    c = make_client()
    register_and_login(c, "Rahul", "rahul@example.com")
    r = c.post("/auth/register", json={"name": "R2", "email": "rahul@example.com", "password": PASSWORD})
    assert r.status_code == 409


def test_wrong_password_and_unknown_email_look_the_same(make_client):
    c = make_client()
    register_and_login(c, "Rahul", "rahul@example.com")
    anon = make_client()
    wrong = anon.post("/auth/login", json={"email": "rahul@example.com", "password": "wrongpass"})
    unknown = anon.post("/auth/login", json={"email": "nobody@example.com", "password": "wrongpass"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_login_me_logout(make_client):
    c = make_client()
    register_and_login(c, "Rahul", "rahul@example.com")
    assert c.get("/auth/me").status_code == 200
    assert c.post("/auth/logout").status_code == 204
    assert c.get("/auth/me").status_code == 401
