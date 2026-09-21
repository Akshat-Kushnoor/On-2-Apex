from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.google import (
    GmailScanResultOut,
    GoogleAuthUrlOut,
    GoogleCalendarSyncResultOut,
    GoogleConnectionStatusOut,
    TaskScheduleRequest,
)
from app.services.google_service import google_service

router = APIRouter()


@router.get("/auth-url", response_model=GoogleAuthUrlOut)
def get_google_auth_url(
    current_user: User = Depends(get_current_user),
):
    return google_service.get_auth_url(user=current_user)


@router.get("/oauth2/callback", response_model=GoogleConnectionStatusOut)
def google_oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    google_service.handle_oauth_callback(db=db, user=current_user, code=code)
    return google_service.get_status(db=db, user=current_user)


@router.get("/status", response_model=GoogleConnectionStatusOut)
def get_google_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return google_service.get_status(db=db, user=current_user)


@router.delete("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_google(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    google_service.disconnect(db=db, user=current_user)


@router.post("/calendar/sync-application/{application_id}", response_model=GoogleCalendarSyncResultOut)
def sync_application_calendar(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return google_service.sync_application_to_calendar(
        db=db,
        user=current_user,
        application_id=application_id,
    )


@router.post("/calendar/sync-task/{task_id}", response_model=GoogleCalendarSyncResultOut)
def sync_task_calendar(
    task_id: str,
    payload: TaskScheduleRequest = TaskScheduleRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return google_service.sync_task_to_calendar(
        db=db,
        user=current_user,
        task_id=task_id,
        scheduled_time=payload.scheduled_time,
        duration_hours=payload.duration_hours,
    )


@router.post("/gmail/scan", response_model=GmailScanResultOut)
def scan_gmail_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return google_service.scan_gmail_for_applications(
        db=db,
        user=current_user,
    )
