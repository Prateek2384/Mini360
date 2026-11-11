import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User
from app.schemas.results import ResultsResponse
from app.services.assessments import get_owned_assessment
from app.services.results import build_results

router = APIRouter(prefix="/assessments", tags=["results"])


@router.get("/{assessment_id}/results", response_model=ResultsResponse)
def get_results(
    assessment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    return build_results(db, assessment)
