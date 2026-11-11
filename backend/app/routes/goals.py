import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import DevelopmentGoal, User
from app.schemas.goals import GoalRead, GoalsUpdate
from app.services.assessments import get_owned_assessment
from app.services.goals import list_goals

router = APIRouter(prefix="/assessments", tags=["goals"])


@router.get("/{assessment_id}/goals", response_model=list[GoalRead])
def get_goals(
    assessment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    return list_goals(db, assessment.id)


@router.put("/{assessment_id}/goals", response_model=list[GoalRead])
def replace_goals(
    assessment_id: uuid.UUID,
    data: GoalsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    db.execute(
        delete(DevelopmentGoal).where(DevelopmentGoal.assessment_id == assessment.id)
    )
    for goal in data.goals:
        db.add(DevelopmentGoal(assessment_id=assessment.id, **goal.model_dump()))
    db.commit()
    return list_goals(db, assessment.id)
