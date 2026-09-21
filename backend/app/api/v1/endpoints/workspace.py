from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.application import (
    ApplicationBrief,
    ApplicationCreateRequest,
    ApplicationEventCreateRequest,
    ApplicationEventOut,
    ApplicationOut,
    ApplicationStageUpdateRequest,
    ApplicationUpdateRequest,
    UpcomingDeadlineOut,
    WorkspaceBoardOut,
)
from app.services.workspace_service import workspace_service

router = APIRouter()


@router.post("/applications", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.create_application(
        db=db,
        user=current_user,
        payload=payload,
    )


@router.get("/board", response_model=WorkspaceBoardOut)
def get_board(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.get_board(
        db=db,
        user=current_user,
    )


@router.get("/applications", response_model=List[ApplicationBrief])
def list_applications(
    stage: Optional[str] = Query(default=None),
    company: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.list_applications(
        db=db,
        user=current_user,
        stage=stage,
        company=company,
        search=search,
    )


@router.get("/upcoming", response_model=List[UpcomingDeadlineOut])
def get_upcoming(
    days_ahead: int = Query(default=14, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.get_upcoming(
        db=db,
        user=current_user,
        days_ahead=days_ahead,
    )


@router.get("/applications/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.get_application_detail(
        db=db,
        user=current_user,
        application_id=application_id,
    )


@router.put("/applications/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: str,
    payload: ApplicationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.update_application(
        db=db,
        user=current_user,
        application_id=application_id,
        payload=payload,
    )


@router.put("/applications/{application_id}/stage", response_model=ApplicationOut)
def update_stage(
    application_id: str,
    payload: ApplicationStageUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.update_stage(
        db=db,
        user=current_user,
        application_id=application_id,
        payload=payload,
    )


@router.post("/applications/{application_id}/events", response_model=ApplicationEventOut, status_code=status.HTTP_201_CREATED)
def add_event(
    application_id: str,
    payload: ApplicationEventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.add_event(
        db=db,
        user=current_user,
        application_id=application_id,
        payload=payload,
    )


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace_service.delete_application(
        db=db,
        user=current_user,
        application_id=application_id,
    )
