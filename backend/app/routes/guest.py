from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.errors import ConflictError
from app.models import User
from app.schemas.responses import GuestSurvey, ResponseSubmit, SubmitResult
from app.services.assessments import now_utc
from app.services.invitations import get_active_invitation
from app.services.responses import get_questions, save_response

router = APIRouter(prefix="/invitations", tags=["guest"])


@router.get("/{token}", response_model=GuestSurvey)
def get_survey(token: str, db: Session = Depends(get_db)):
    invitation, assessment = get_active_invitation(db, token)
    leader = db.get(User, assessment.creator_user_id)
    return GuestSurvey(
        assessment_title=assessment.title,
        leader_name=leader.name,
        expires_at=invitation.expires_at,
        questions=get_questions(db, assessment.id),
    )


@router.post("/{token}/submit", response_model=SubmitResult, status_code=201)
def submit(token: str, data: ResponseSubmit, db: Session = Depends(get_db)):
    invitation, assessment = get_active_invitation(db, token)
    try:
        response = save_response(
            db, assessment.id, data.answers, "rater", invitation.id
        )
        invitation.status = "submitted"
        invitation.submitted_at = now_utc()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("This invitation has already been used")
    db.refresh(response)
    return SubmitResult(response_id=response.id, submitted_at=response.submitted_at)
