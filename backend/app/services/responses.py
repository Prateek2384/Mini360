import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.models import Answer, Question, Response
from app.schemas.responses import AnswerIn


def get_questions(db: Session, assessment_id: uuid.UUID) -> list[Question]:
    return list(
        db.scalars(
            select(Question)
            .where(Question.assessment_id == assessment_id)
            .order_by(Question.position)
        ).all()
    )


def save_response(
    db: Session,
    assessment_id: uuid.UUID,
    answers: list[AnswerIn],
    response_type: str,
    invitation_id: uuid.UUID | None = None,
) -> Response:
    expected = {q.id for q in get_questions(db, assessment_id)}
    submitted = [a.question_id for a in answers]
    if len(submitted) != len(set(submitted)):
        raise BadRequestError("Each question can be answered only once")
    if set(submitted) != expected:
        raise BadRequestError("All questions of this assessment must be answered")

    response = Response(
        assessment_id=assessment_id,
        response_type=response_type,
        invitation_id=invitation_id,
    )
    db.add(response)
    db.flush()
    for a in answers:
        db.add(Answer(response_id=response.id, question_id=a.question_id, score=a.score))
    db.flush()
    return response
