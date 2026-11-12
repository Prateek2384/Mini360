import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.errors import ConflictError
from app.models import User
from app.schemas.responses import QuestionRead, ResponseSubmit, SubmitResult
from app.services.assessments import get_owned_assessment, now_utc
from app.services.responses import get_questions, save_response

router = APIRouter(prefix="/assessments", tags=["self-assessment"])


@router.get("/{assessment_id}/questions", response_model=list[QuestionRead])
def list_questions(
    assessment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    return get_questions(db, assessment.id)


@router.post(
    "/{assessment_id}/self-response", response_model=SubmitResult, status_code=201
)
def submit_self_response(
    assessment_id: uuid.UUID,
    data: ResponseSubmit,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    if assessment.status == "closed":
        raise ConflictError("Assessment is closed")
    if assessment.self_completed_at is not None:
        raise ConflictError("Self-assessment already submitted")
    try:
        response = save_response(db, assessment.id, data.answers, "self")
        assessment.self_completed_at = now_utc()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Self-assessment already submitted") from None
    db.refresh(response)
    return SubmitResult(response_id=response.id, submitted_at=response.submitted_at)
