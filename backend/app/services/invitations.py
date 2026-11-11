from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError, ConflictError, NotFoundError
from app.core.tokens import hash_token
from app.models import Assessment, Invitation
from app.services.assessments import now_utc, refresh_status


def get_active_invitation(db: Session, token: str) -> tuple[Invitation, Assessment]:
    invitation = db.scalar(
        select(Invitation).where(Invitation.token_hash == hash_token(token))
    )
    if invitation is None:
        raise NotFoundError("Invitation not found")

    assessment = db.get(Assessment, invitation.assessment_id)
    refresh_status(db, assessment)

    if invitation.status == "submitted":
        raise ConflictError("This invitation has already been used")

    expired = (
        invitation.status == "expired"
        or invitation.expires_at <= now_utc()
        or assessment.status != "open"
    )
    if expired:
        if invitation.status != "expired":
            invitation.status = "expired"
            db.commit()
        raise AppError(410, "expired", "This invitation has expired")

    return invitation, assessment
