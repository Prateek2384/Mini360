import uuid

import pytest

from tests.helpers import (
    RATER_SCORES,
    SELF_SCORES,
    close_assessment,
    create_open_assessment,
    invite,
    register_and_login,
    run_sql,
    submit_guest,
    submit_self,
)


@pytest.fixture
def scenario(make_client):
    def _build(raters: int, close: bool):
        leader = make_client()
        register_and_login(leader, "Rahul", "rahul@example.com")
        aid = create_open_assessment(leader)
        submit_self(leader, aid, SELF_SCORES)
        tokens = invite(leader, aid, ["amit@example.com", "neha@example.com", "priya@example.com"])
        guest = make_client()
        for token, scores in zip(tokens[:raters], RATER_SCORES[:raters]):
            assert submit_guest(guest, token, scores).status_code == 201
        if close:
            close_assessment(aid)
        return leader, aid, tokens, guest

    return _build


@pytest.mark.parametrize("raters", [0, 1, 2])
def test_results_locked_below_three_responses(scenario, raters):
    leader, aid, _, _ = scenario(raters, close=True)
    r = leader.get(f"/assessments/{aid}/results")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "results_locked"
    assert "others_mean" not in r.text
    assert leader.get(f"/assessments/{aid}/report.pdf").status_code == 409


def test_results_locked_while_survey_open(scenario):
    leader, aid, _, _ = scenario(3, close=False)
    r = leader.get(f"/assessments/{aid}/results")
    assert r.status_code == 409
    assert "closes" in r.json()["error"]["message"]


def test_results_match_hand_calculation_and_hide_identities(scenario):
    leader, aid, _, _ = scenario(3, close=True)
    r = leader.get(f"/assessments/{aid}/results")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["overall"]["others_mean"] == pytest.approx(3.7)
    assert data["overall"]["self_score"] == pytest.approx(4.1)
    assert data["overall"]["gap"] == pytest.approx(0.4)
    assert [f["position"] for f in data["focus_areas"]] == [9, 2]
    assert "@" not in r.text


def test_pdf_report_downloads(scenario):
    leader, aid, _, _ = scenario(3, close=True)
    r = leader.get(f"/assessments/{aid}/report.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/pdf")
    assert r.content[:5] == b"%PDF-"


def test_other_leader_cannot_access_by_changing_id(scenario, make_client):
    _, aid, _, _ = scenario(3, close=True)
    other = make_client()
    register_and_login(other, "Neha", "neha.leader@example.com")
    for path in ["status", "results", "questions", "report.pdf"]:
        assert other.get(f"/assessments/{aid}/{path}").status_code == 404
    r = other.post(f"/assessments/{aid}/invitations", json={"emails": ["x@example.com"]})
    assert r.status_code == 404


def test_invitation_can_submit_only_once(scenario):
    _, _, tokens, guest = scenario(1, close=False)
    assert guest.get(f"/invitations/{tokens[0]}").status_code == 409
    fake = {"answers": [{"question_id": str(uuid.uuid4()), "score": 3}]}
    assert guest.post(f"/invitations/{tokens[0]}/submit", json=fake).status_code == 409


def test_invalid_token_returns_404(make_client):
    assert make_client().get("/invitations/not-a-real-token").status_code == 404


def test_expired_invitation_is_rejected(scenario):
    _, aid, tokens, guest = scenario(0, close=False)
    run_sql(
        "UPDATE invitations SET expires_at = now() - interval '1 minute' WHERE assessment_id = :id",
        id=aid,
    )
    r = guest.get(f"/invitations/{tokens[0]}")
    assert r.status_code == 410
    assert r.json()["error"]["code"] == "expired"


def test_closed_survey_rejects_guests(scenario):
    _, _, tokens, guest = scenario(0, close=True)
    assert guest.get(f"/invitations/{tokens[0]}").status_code == 410


def test_unauthenticated_requests_are_rejected(make_client):
    c = make_client()
    assert c.get("/assessments").status_code == 401
    assert c.post("/assessments", json={"title": "x"}).status_code == 401
