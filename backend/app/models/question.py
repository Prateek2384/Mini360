import uuid

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, uuid_pk


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint(
            "category IN ('communication', 'collaboration', 'accountability')",
            name="category_valid",
        ),
        UniqueConstraint("assessment_id", "position"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str] = mapped_column(String(30))
    text: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(SmallInteger)
