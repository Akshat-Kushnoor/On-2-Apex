from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import (
    LearningPlanCreateRequest,
    LearningPlanOut,
    LearningTaskOut,
    TaskStatusUpdateRequest,
)
from app.services.learning_engine import learning_engine

router = APIRouter()


@router.post("/plan", response_model=LearningPlanOut, status_code=status.HTTP_201_CREATED)
def create_learning_plan(
    payload: LearningPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return learning_engine.create_learning_plan(
        db=db,
        user=current_user,
        request=payload,
    )


@router.get("/plan/active", response_model=LearningPlanOut)
def get_active_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = learning_engine.get_active_plan(db=db, user=current_user)
    if not plan:
        raise AppException(
            message="No active learning plan found.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return plan


@router.get("/plans", response_model=List[LearningPlanOut])
def get_user_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return learning_engine.get_user_plans(db=db, user=current_user)


@router.get("/plan/{plan_id}", response_model=LearningPlanOut)
def get_plan_by_id(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return learning_engine.get_plan_by_id(db=db, user=current_user, plan_id=plan_id)


@router.put("/tasks/{task_id}", response_model=LearningTaskOut)
def update_task_status(
    task_id: str,
    payload: TaskStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return learning_engine.update_task_status(
        db=db,
        user=current_user,
        task_id=task_id,
        new_status=payload.status,
        evidence=payload.evidence,
    )
