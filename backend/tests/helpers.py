from datetime import UTC, datetime, timedelta

from sqlalchemy import text

from app.core.database import engine

PASSWORD = "secret123"
SELF_SCORES = [5, 5, 4, 4, 4, 3, 5, 4, 3, 4]
RATER_SCORES = [
    [4, 3, 4, 3, 5, 4, 4, 3, 2, 4],
    [3, 3, 5, 4, 4, 4, 3, 4, 2, 3],
    [5, 3, 3, 5, 3, 5, 4, 5, 2, 5],
]


def future_iso(days: int = 7) -> str:
    return (datetime.now(UTC) + timedelta(days=days)).isoformat()


def register_and_login(client, name: str, email: str) -> None:
    r = client.post("/auth/register", json={"name": name, "email": email, "password": PASSWORD})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text


def create_open_assessment(client, title: str = "Test assessment") -> str:
    r = client.post("/assessments", json={"title": title, "closes_at": future_iso()})
    assert r.status_code == 201, r.text
    aid = r.json()["id"]
    r = client.post(f"/assessments/{aid}/launch")
    assert r.status_code == 200, r.text
    return aid


def build_answers(questions: list[dict], scores: list[int]) -> dict:
    by_pos = {q["position"]: q["id"] for q in questions}
    return {"answers": [{"question_id": by_pos[i + 1], "score": s} for i, s in enumerate(scores)]}


def submit_self(client, aid: str, scores: list[int]) -> None:
    questions = client.get(f"/assessments/{aid}/questions").json()
    r = client.post(f"/assessments/{aid}/self-response", json=build_answers(questions, scores))
    assert r.status_code == 201, r.text


def invite(client, aid: str, emails: list[str]) -> list[str]:
    r = client.post(f"/assessments/{aid}/invitations", json={"emails": emails})
    assert r.status_code == 201, r.text
    return [i["invite_url"].rsplit("/", 1)[1] for i in r.json()["invitations"]]


def submit_guest(client, token: str, scores: list[int]):
    survey = client.get(f"/invitations/{token}")
    assert survey.status_code == 200, survey.text
    return client.post(
        f"/invitations/{token}/submit", json=build_answers(survey.json()["questions"], scores)
    )


def run_sql(sql: str, **params) -> None:
    with engine.begin() as conn:
        conn.execute(text(sql), params)


def close_assessment(aid: str) -> None:
    run_sql("UPDATE assessments SET closes_at = now() - interval '1 minute' WHERE id = :id", id=aid)
