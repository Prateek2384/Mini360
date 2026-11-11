import uuid
from types import SimpleNamespace

import pytest

from app.services.scoring import compute_results
from tests.helpers import RATER_SCORES, SELF_SCORES

CATEGORIES = ["communication"] * 4 + ["collaboration"] * 3 + ["accountability"] * 3


def make_questions():
    return [
        SimpleNamespace(id=uuid.uuid4(), position=i + 1, category=CATEGORIES[i], text=f"Q{i + 1}")
        for i in range(10)
    ]


def scores_for(questions):
    self_scores = {q.id: SELF_SCORES[i] for i, q in enumerate(questions)}
    rater_scores = {q.id: [r[i] for r in RATER_SCORES] for i, q in enumerate(questions)}
    return self_scores, rater_scores


def test_matches_hand_calculation():
    qs = make_questions()
    res = compute_results(qs, *scores_for(qs))
    assert res["overall"]["others_mean"] == pytest.approx(3.7)
    assert res["overall"]["self_score"] == pytest.approx(4.1)
    assert res["overall"]["gap"] == pytest.approx(0.4)
    cats = {c["category"]: c for c in res["categories"]}
    assert cats["communication"]["others_mean"] == pytest.approx(3.75)
    assert cats["communication"]["self_score"] == pytest.approx(4.5)
    assert cats["collaboration"]["others_mean"] == pytest.approx(4.0)
    assert cats["accountability"]["others_mean"] == pytest.approx(10 / 3)
    assert cats["accountability"]["self_score"] == pytest.approx(11 / 3)
    assert [f["position"] for f in res["focus_areas"]] == [9, 2]


def test_missing_self_response_gives_null_gaps():
    qs = make_questions()
    _, rater_scores = scores_for(qs)
    res = compute_results(qs, {}, rater_scores)
    assert res["overall"]["self_score"] is None
    assert res["overall"]["gap"] is None
    assert all(c["gap"] is None for c in res["categories"])


def test_focus_area_ties_break_by_position():
    qs = make_questions()
    res = compute_results(qs, {}, {q.id: [3, 3, 3] for q in qs})
    assert [f["position"] for f in res["focus_areas"]] == [1, 2]
