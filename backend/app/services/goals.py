import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DevelopmentGoal


def list_goals(db: Session, assessment_id: uuid.UUID) -> list[DevelopmentGoal]:
    return list(
        db.scalars(
            select(DevelopmentGoal)
            .where(DevelopmentGoal.assessment_id == assessment_id)
            .order_by(DevelopmentGoal.created_at, DevelopmentGoal.title)
        ).all()
    )
