from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Answer, Assessment, Response
from app.services.assessments import rater_response_count
from app.services.responses import get_questions
from app.services.scoring import compute_results

FOCUS_NOTE = (
    "Focus areas are simple suggestions based on the lowest-rated items, "
    "not validated psychological findings."
)


def build_results(db: Session, assessment: Assessment) -> dict:
    count = rater_response_count(db, assessment.id)
    if count < assessment.min_responses:
        raise AppError(
            409,
            "results_locked",
            f"Results unlock after {assessment.min_responses} responses.",
        )
    if assessment.status != "closed":
        raise AppError(409, "results_locked", "Results unlock after the survey closes.")

    rows = db.execute(
        select(Response.response_type, Answer.question_id, Answer.score)
        .join(Answer, Answer.response_id == Response.id)
        .where(Response.assessment_id == assessment.id)
    ).all()
    self_scores = {}
    rater_scores = defaultdict(list)
    for response_type, question_id, score in rows:
        if response_type == "self":
            self_scores[question_id] = score
        else:
            rater_scores[question_id].append(score)

    data = compute_results(get_questions(db, assessment.id), self_scores, rater_scores)
    data.update(
        assessment_id=assessment.id,
        title=assessment.title,
        rater_response_count=count,
        focus_note=FOCUS_NOTE,
    )
    return data
