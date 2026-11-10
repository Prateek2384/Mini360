import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, uuid_pk


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        CheckConstraint(
            "response_type IN ('self', 'rater')", name="response_type_valid"
        ),
        CheckConstraint(
            "(response_type = 'self' AND invitation_id IS NULL) "
            "OR (response_type = 'rater' AND invitation_id IS NOT NULL)",
            name="type_matches_invitation",
        ),
        Index(
            "uq_responses_one_self_per_assessment",
            "assessment_id",
            unique=True,
            postgresql_where=text("response_type = 'self'"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True
    )
    response_type: Mapped[str] = mapped_column(String(10))
    invitation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("invitations.id", ondelete="CASCADE"), unique=True
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
