from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview import (
    InterviewEvaluateRequest,
    InterviewScorecardOut,
    InterviewSessionBrief,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.services.interview_engine import interview_engine

router = APIRouter()


@router.post("/start", response_model=InterviewStartResponse)
def start_interview(
    payload: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
):
    questions = interview_engine.get_questions_for_role(payload.position)
    return InterviewStartResponse(
        position=payload.position.strip(),
        questions=questions,
    )


@router.post("/evaluate", response_model=InterviewScorecardOut, status_code=status.HTTP_201_CREATED)
def evaluate_interview(
    payload: InterviewEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = interview_engine.evaluate_session(
        payload=payload,
        current_user=current_user,
        db=db,
    )
    return session


@router.get("/latest", response_model=Optional[InterviewScorecardOut])
def get_latest_interview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = interview_engine.get_latest_session(user_id=current_user.id, db=db)
    return session


@router.get("/history", response_model=List[InterviewSessionBrief])
def list_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = interview_engine.list_user_sessions(user_id=current_user.id, db=db)
    return sessions
