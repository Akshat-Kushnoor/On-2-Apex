from typing import List, Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.resume import (
    GeneratedResumeBrief,
    GeneratedResumeOut,
    ResumeApplyRequest,
    ResumeGenerateRequest,
    ResumeUpdateRequest,
)
from app.services.resume_engine import resume_engine

router = APIRouter()


@router.post("/generate", response_model=GeneratedResumeOut, status_code=status.HTTP_201_CREATED)
def generate_resume(
    payload: ResumeGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return resume_engine.generate_resume(
        db=db,
        user=current_user,
        request=payload,
    )


@router.get("", response_model=List[GeneratedResumeBrief])
def list_resumes(
    tag: Optional[str] = None,
    position: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return resume_engine.list_resumes(
        db=db,
        user=current_user,
        tag=tag,
        position=position,
    )


@router.get("/{resume_id}", response_model=GeneratedResumeOut)
def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return resume_engine.get_resume_by_id(
        db=db,
        user=current_user,
        resume_id=resume_id,
    )


@router.put("/{resume_id}", response_model=GeneratedResumeOut)
def update_resume(
    resume_id: str,
    payload: ResumeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return resume_engine.update_resume(
        db=db,
        user=current_user,
        resume_id=resume_id,
        payload=payload,
    )


@router.post("/{resume_id}/apply", response_model=GeneratedResumeOut)
def record_application(
    resume_id: str,
    payload: ResumeApplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return resume_engine.record_application(
        db=db,
        user=current_user,
        resume_id=resume_id,
        payload=payload,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume_engine.delete_resume(
        db=db,
        user=current_user,
        resume_id=resume_id,
    )


@router.get("/{resume_id}/markdown", response_class=PlainTextResponse)
def get_resume_markdown(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = resume_engine.get_resume_by_id(
        db=db,
        user=current_user,
        resume_id=resume_id,
    )
    return PlainTextResponse(content=resume.markdown, media_type="text/markdown")


@router.get("/{resume_id}/latex", response_class=PlainTextResponse)
def get_resume_latex(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = resume_engine.get_resume_by_id(
        db=db,
        user=current_user,
        resume_id=resume_id,
    )
    return PlainTextResponse(content=resume.latex, media_type="text/x-tex")
