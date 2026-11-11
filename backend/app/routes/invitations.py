import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_db
from app.core.errors import BadRequestError, ConflictError
from app.core.tokens import generate_invite_token
from app.models import Invitation, User
from app.schemas.invitations import (
    InvitationCreate,
    InvitationCreateResult,
    InvitationLink,
)
from app.services.assessments import get_owned_assessment

router = APIRouter(prefix="/assessments", tags=["invitations"])


@router.post(
    "/{assessment_id}/invitations",
    response_model=InvitationCreateResult,
    status_code=201,
)
def create_invitations(
    assessment_id: uuid.UUID,
    data: InvitationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    if assessment.status != "open":
        raise ConflictError("Assessment must be open to invite raters")

    emails = list(dict.fromkeys(e.strip().lower() for e in data.emails))
    if user.email in emails:
        raise BadRequestError("You cannot invite yourself as a rater")

    existing = set(
        db.scalars(
            select(Invitation.rater_email).where(
                Invitation.assessment_id == assessment.id,
                Invitation.rater_email.in_(emails),
            )
        ).all()
    )
    if existing:
        raise ConflictError(f"Already invited: {', '.join(sorted(existing))}")

    created: list[tuple[Invitation, str]] = []
    try:
        for email in emails:
            token, token_hash = generate_invite_token()
            invitation = Invitation(
                assessment_id=assessment.id,
                rater_email=email,
                token_hash=token_hash,
                expires_at=assessment.closes_at,
            )
            db.add(invitation)
            db.flush()
            created.append((invitation, token))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("One or more emails were already invited")

    return InvitationCreateResult(
        invitations=[
            InvitationLink(
                id=inv.id,
                rater_email=inv.rater_email,
                invite_url=f"{settings.frontend_url}/invite/{token}",
                expires_at=inv.expires_at,
            )
            for inv, token in created
        ]
    )
