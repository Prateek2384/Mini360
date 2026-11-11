import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.errors import BadRequestError, ConflictError
from app.models import Assessment, User
from app.schemas.assessments import (
    AssessmentCreate,
    AssessmentLaunch,
    AssessmentRead,
    AssessmentStatus,
)
from app.services.assessments import (
    create_assessment,
    get_owned_assessment,
    invitation_count,
    now_utc,
    rater_response_count,
    refresh_status,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


def to_read(db: Session, a: Assessment) -> AssessmentRead:
    return AssessmentRead(
        id=a.id,
        title=a.title,
        status=a.status,
        min_responses=a.min_responses,
        closes_at=a.closes_at,
        closed_at=a.closed_at,
        self_completed_at=a.self_completed_at,
        created_at=a.created_at,
        rater_response_count=rater_response_count(db, a.id),
    )


@router.post("", response_model=AssessmentRead, status_code=201)
def create(
    data: AssessmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.closes_at is not None and data.closes_at <= now_utc():
        raise BadRequestError("closes_at must be in the future")
    assessment = create_assessment(db, user, data.title, data.closes_at)
    return to_read(db, assessment)


@router.get("", response_model=list[AssessmentRead])
def list_mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessments = db.scalars(
        select(Assessment)
        .where(Assessment.creator_user_id == user.id)
        .order_by(Assessment.created_at.desc())
    ).all()
    for a in assessments:
        refresh_status(db, a)
    return [to_read(db, a) for a in assessments]


@router.post("/{assessment_id}/launch", response_model=AssessmentRead)
def launch(
    assessment_id: uuid.UUID,
    data: AssessmentLaunch | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    if assessment.status != "draft":
        raise ConflictError("Only draft assessments can be launched")
    closes_at = (data.closes_at if data and data.closes_at else None) or assessment.closes_at
    if closes_at is None:
        raise BadRequestError("closes_at is required to launch")
    if closes_at <= now_utc():
        raise BadRequestError("closes_at must be in the future")
    assessment.closes_at = closes_at
    assessment.status = "open"
    db.commit()
    db.refresh(assessment)
    return to_read(db, assessment)


@router.get("/{assessment_id}/status", response_model=AssessmentStatus)
def status(
    assessment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = get_owned_assessment(db, assessment_id, user)
    count = rater_response_count(db, a.id)
    return AssessmentStatus(
        id=a.id,
        status=a.status,
        closes_at=a.closes_at,
        closed_at=a.closed_at,
        min_responses=a.min_responses,
        invitation_count=invitation_count(db, a.id),
        rater_response_count=count,
        self_completed=a.self_completed_at is not None,
        results_unlocked=a.status == "closed" and count >= a.min_responses,
    )
