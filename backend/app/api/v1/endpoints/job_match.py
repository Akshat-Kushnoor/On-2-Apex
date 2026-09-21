from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.db.session import get_db
from app.models.job_match import JobMatch
from app.models.user import User
from app.schemas.job_match import JobMatchOut, JobMatchRequest
from app.services.skill_gap_engine import skill_gap_engine

router = APIRouter()


@router.post("/{job_id}/compare", response_model=JobMatchOut, status_code=status.HTTP_200_OK)
def compare_student_to_job(
    job_id: str,
    payload: JobMatchRequest = JobMatchRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return skill_gap_engine.compare_student_to_job(
        db=db,
        user=current_user,
        job_id=job_id,
        force_recompute=payload.force_recompute,
    )


@router.get("/{job_id}/match", response_model=JobMatchOut)
def get_job_match(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match_record = (
        db.query(JobMatch)
        .filter(JobMatch.job_id == job_id, JobMatch.user_id == current_user.id)
        .order_by(JobMatch.created_at.desc())
        .first()
    )
    if not match_record:
        raise AppException(
            message="No match analysis found for this job. Please run compare first.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return match_record
