from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.db.session import get_db
from app.models.job_analysis import JobAnalysis
from app.models.user import User
from app.schemas.job_analysis import (
    JDAnalyzeRequest,
    StructuredRequirementsOut,
)
from app.services.jd_analyzer import jd_analyzer

router = APIRouter()


@router.post("/analyze", response_model=StructuredRequirementsOut, status_code=status.HTTP_200_OK)
def analyze_job_description(
    payload: JDAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return jd_analyzer.analyze_job_description(
        db=db,
        user_id=current_user.id,
        request=payload,
    )


@router.get("/{job_id}/analysis", response_model=StructuredRequirementsOut)
def get_job_analysis(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(JobAnalysis)
        .filter(JobAnalysis.job_id == job_id, JobAnalysis.user_id == current_user.id)
        .order_by(JobAnalysis.created_at.desc())
        .first()
    )
    if not analysis:
        raise AppException(
            message="No analysis found for this job. Please trigger analysis first.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    out = StructuredRequirementsOut.model_validate(analysis)
    out.cached = True
    return out
