import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import User
from app.services.assessments import get_owned_assessment
from app.services.goals import list_goals
from app.services.report import render_report_pdf
from app.services.results import build_results

router = APIRouter(prefix="/assessments", tags=["report"])


@router.get(
    "/{assessment_id}/report.pdf",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
)
def download_report(
    assessment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = get_owned_assessment(db, assessment_id, user)
    results = build_results(db, assessment)
    pdf = render_report_pdf(assessment, user.name, results, list_goals(db, assessment.id))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="mini360-report.pdf"'},
    )
