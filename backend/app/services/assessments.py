import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models import Assessment, Invitation, Question, Response, User
from app.services.question_bank import QUESTION_BANK


def now_utc() -> datetime:
    return datetime.now(UTC)


def create_assessment(
    db: Session, user: User, title: str, closes_at: datetime | None
) -> Assessment:
    assessment = Assessment(
        creator_user_id=user.id, title=title.strip(), closes_at=closes_at
    )
    db.add(assessment)
    db.flush()
    for position, (category, text) in enumerate(QUESTION_BANK, start=1):
        db.add(
            Question(
                assessment_id=assessment.id,
                category=category,
                text=text,
                position=position,
            )
        )
    db.commit()
    db.refresh(assessment)
    return assessment


def refresh_status(db: Session, assessment: Assessment) -> None:
    if (
        assessment.status == "open"
        and assessment.closes_at is not None
        and assessment.closes_at <= now_utc()
    ):
        assessment.status = "closed"
        assessment.closed_at = assessment.closes_at
        db.commit()
        db.refresh(assessment)


def get_owned_assessment(
    db: Session, assessment_id: uuid.UUID, user: User
) -> Assessment:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None or assessment.creator_user_id != user.id:
        raise NotFoundError("Assessment not found")
    refresh_status(db, assessment)
    return assessment


def rater_response_count(db: Session, assessment_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Response)
        .where(
            Response.assessment_id == assessment_id,
            Response.response_type == "rater",
        )
    ) or 0


def invitation_count(db: Session, assessment_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Invitation)
        .where(Invitation.assessment_id == assessment_id)
    ) or 0
