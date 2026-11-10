import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, uuid_pk


class DevelopmentGoal(Base):
    __tablename__ = "development_goals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'done')", name="status_valid"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(20), server_default="not_started")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
