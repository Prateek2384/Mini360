import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, uuid_pk


class Assessment(Base):
    __tablename__ = "assessments"
    """Constraint	Rule	PRD se connection
    status_valid	Status sirf draft, open ya closed ho sakta hai	Tumhare ER ka enum
    launched_requires_closes_at	Draft ke alawa koi bhi status ho, to closing date zaroori hai	FR-02: survey closing date ke saath launch hota hai
    closed_at_matches_status	Status closed hai, to closed_at bhara hona chahiye. Aur closed_at bhara hai, to status closed hi hona chahiye	Dono kabhi ek-doosre se alag nahi ho sakte
    min_responses_at_least_3	Threshold kabhi 3 se kam nahi ho sakta	PRD ka privacy rule"""
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'open', 'closed')", name="status_valid"
        ),
        CheckConstraint(
            "status = 'draft' OR closes_at IS NOT NULL",
            name="launched_requires_closes_at",
        ),
        CheckConstraint(
            "(status = 'closed') = (closed_at IS NOT NULL)",
            name="closed_at_matches_status",
        ),
        CheckConstraint("min_responses >= 3", name="min_responses_at_least_3"),
    )

    """ForeignKey("users.id")	Is column mein sirf wahi value aa sakti hai jo users table ke id mein exist karti ho. Koi “bhoot” user ka assessment nahi ban sakta
    ondelete="CASCADE"	Agar user delete hua, to uske saare assessments bhi apne aap delete ho jaayenge
    index=True	“Rahul ke saare assessments dikhao” wali query tez chalegi. Dashboard yahi query har baar chalayega"""
    id: Mapped[uuid.UUID] = uuid_pk()
    creator_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), server_default="draft")
    min_responses: Mapped[int] = mapped_column(
        SmallInteger, server_default=text("3")
    )
    closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    self_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
