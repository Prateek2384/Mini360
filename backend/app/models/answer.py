import uuid

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, uuid_pk


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("response_id", "question_id"),
        CheckConstraint("score BETWEEN 1 AND 5", name="score_range"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    response_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("responses.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True
    )
    score: Mapped[int] = mapped_column(SmallInteger)
