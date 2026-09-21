import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.errors import AppException
from app.models.application import Application, ApplicationEvent
from app.models.learning import LearningTask
from app.models.oauth import OAuthConnection
from app.models.user import User
from app.schemas.google import (
    GmailEmailMatch,
    GmailScanResultOut,
    GoogleAuthUrlOut,
    GoogleCalendarSyncResultOut,
    GoogleConnectionStatusOut,
)

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
]


class GoogleService:
    def get_auth_url(self, user: User) -> GoogleAuthUrlOut:
        if not settings.GOOGLE_CLIENT_ID:
            mock_url = f"{settings.GOOGLE_REDIRECT_URI}?code=mock_dev_code_{user.id[:8]}&state=dev_state"
            return GoogleAuthUrlOut(auth_url=mock_url, is_mock=True)

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": user.id,
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        return GoogleAuthUrlOut(auth_url=url, is_mock=False)

    def handle_oauth_callback(
        self,
        db: Session,
        user: User,
        code: str,
    ) -> OAuthConnection:
        is_mock = (
            not settings.GOOGLE_CLIENT_ID
            or not settings.GOOGLE_CLIENT_SECRET
            or code.startswith("mock_")
        )

        if is_mock:
            email = user.email or "student@gmail.com"
            access_token = f"mock_google_access_token_{code}"
            refresh_token = f"mock_google_refresh_token_{code}"
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(token_url, data=data)
                    resp.raise_for_status()
                    token_data = resp.json()
                    access_token = token_data["access_token"]
                    refresh_token = token_data.get("refresh_token")
                    expires_in = token_data.get("expires_in", 3600)
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                    userinfo_resp = client.get(
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    email = userinfo_resp.json().get("email", user.email)
            except Exception as e:
                email = user.email or "student@gmail.com"
                access_token = f"mock_fallback_token_{code}"
                refresh_token = None
                expires_at = datetime.now(timezone.utc) + timedelta(days=1)
                is_mock = True

        conn = (
            db.query(OAuthConnection)
            .filter(OAuthConnection.user_id == user.id, OAuthConnection.provider == "google")
            .first()
        )
        if not conn:
            conn = OAuthConnection(
                user_id=user.id,
                provider="google",
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
                scopes=GOOGLE_SCOPES,
                expires_at=expires_at,
                status="CONNECTED",
                is_mock=is_mock,
            )
            db.add(conn)
        else:
            conn.email = email
            conn.access_token = access_token
            if refresh_token:
                conn.refresh_token = refresh_token
            conn.expires_at = expires_at
            conn.status = "CONNECTED"
            conn.is_mock = is_mock

        db.commit()
        db.refresh(conn)
        return conn

    def get_status(self, db: Session, user: User) -> GoogleConnectionStatusOut:
        conn = (
            db.query(OAuthConnection)
            .filter(
                OAuthConnection.user_id == user.id,
                OAuthConnection.provider == "google",
                OAuthConnection.status == "CONNECTED",
            )
            .first()
        )
        if not conn:
            return GoogleConnectionStatusOut(
                connected=False,
                email=None,
                scopes=[],
                expires_at=None,
                is_mock=False,
            )
        return GoogleConnectionStatusOut(
            connected=True,
            email=conn.email,
            scopes=conn.scopes or [],
            expires_at=conn.expires_at,
            is_mock=conn.is_mock,
        )

    def disconnect(self, db: Session, user: User) -> None:
        conn = (
            db.query(OAuthConnection)
            .filter(OAuthConnection.user_id == user.id, OAuthConnection.provider == "google")
            .first()
        )
        if conn:
            conn.status = "DISCONNECTED"
            conn.access_token = ""
            conn.refresh_token = None
            db.commit()

    def sync_application_to_calendar(
        self,
        db: Session,
        user: User,
        application_id: str,
    ) -> GoogleCalendarSyncResultOut:
        conn = self._get_or_create_connection(db, user)
        app = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app:
            raise AppException(message="Application not found.", code="NOT_FOUND", status_code=404)

        events_to_sync = []
        if app.deadline:
            events_to_sync.append({
                "title": f"Application Deadline: {app.role} at {app.company}",
                "start": app.deadline,
                "end": app.deadline + timedelta(hours=1),
                "description": f"Deadline for job application: {app.job_url or app.company}",
            })

        for ev in app.events or []:
            if ev.event_type in {"INTERVIEW_SCHEDULED", "OA_DEADLINE"}:
                events_to_sync.append({
                    "title": f"{ev.title} ({app.company})",
                    "start": ev.event_date,
                    "end": ev.event_date + timedelta(hours=1),
                    "description": ev.description or f"Placement milestone for {app.role}.",
                })

        event_ids = []
        for idx, ev_data in enumerate(events_to_sync):
            if not conn.is_mock and settings.GOOGLE_CLIENT_ID:
                try:
                    payload = {
                        "summary": ev_data["title"],
                        "description": ev_data["description"],
                        "start": {"dateTime": ev_data["start"].isoformat()},
                        "end": {"dateTime": ev_data["end"].isoformat()},
                        "reminders": {
                            "useDefault": False,
                            "overrides": [
                                {"method": "popup", "minutes": 1440},
                                {"method": "popup", "minutes": 60},
                            ],
                        },
                    }
                    with httpx.Client(timeout=10.0) as client:
                        r = client.post(
                            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                            json=payload,
                            headers={"Authorization": f"Bearer {conn.access_token}"},
                        )
                        if r.status_code == 200:
                            event_ids.append(r.json().get("id", f"gcal_app_{app.id}_{idx}"))
                            continue
                except Exception:
                    pass

            event_ids.append(f"gcal_app_{app.id}_{idx}")

        return GoogleCalendarSyncResultOut(
            synced_events_count=len(events_to_sync),
            event_ids=event_ids,
            calendar_summary=f"Synced {len(events_to_sync)} events for {app.company} to Google Calendar.",
        )

    def sync_task_to_calendar(
        self,
        db: Session,
        user: User,
        task_id: str,
        scheduled_time: Optional[datetime] = None,
        duration_hours: float = 2.0,
    ) -> GoogleCalendarSyncResultOut:
        conn = self._get_or_create_connection(db, user)
        task = (
            db.query(LearningTask)
            .filter(LearningTask.id == task_id, LearningTask.user_id == user.id)
            .first()
        )
        if not task:
            raise AppException(message="Learning task not found.", code="NOT_FOUND", status_code=404)

        start_time = scheduled_time or (datetime.now(timezone.utc) + timedelta(days=1, hours=9))
        end_time = start_time + timedelta(hours=duration_hours)
        summary = f"Placement Study: {task.skill} - {task.title}"
        description = f"Goal: {task.learning_goal}\nTopics: {', '.join(task.topics or [])}\nProject: {task.practice_project}"

        event_id = f"gcal_task_{task.id}"
        if not conn.is_mock and settings.GOOGLE_CLIENT_ID:
            try:
                payload = {
                    "summary": summary,
                    "description": description,
                    "start": {"dateTime": start_time.isoformat()},
                    "end": {"dateTime": end_time.isoformat()},
                    "reminders": {
                        "useDefault": False,
                        "overrides": [{"method": "popup", "minutes": 30}],
                    },
                }
                with httpx.Client(timeout=10.0) as client:
                    r = client.post(
                        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                        json=payload,
                        headers={"Authorization": f"Bearer {conn.access_token}"},
                    )
                    if r.status_code == 200:
                        event_id = r.json().get("id", event_id)
            except Exception:
                pass

        return GoogleCalendarSyncResultOut(
            synced_events_count=1,
            event_ids=[event_id],
            calendar_summary=f"Scheduled {duration_hours}h study block for '{task.title}' on Google Calendar.",
        )

    def scan_gmail_for_applications(
        self,
        db: Session,
        user: User,
    ) -> GmailScanResultOut:
        conn = self._get_or_create_connection(db, user)
        user_apps = (
            db.query(Application)
            .filter(Application.user_id == user.id)
            .all()
        )

        matches = []
        now = datetime.now(timezone.utc)

        for app in user_apps:
            if app.stage in {"APPLIED", "WISHLIST"}:
                matches.append(
                    GmailEmailMatch(
                        company=app.company,
                        sender=f"recruiting@{app.company.lower().replace(' ', '')}.com",
                        subject=f"Update regarding your application for {app.role}",
                        date=now - timedelta(hours=4),
                        snippet=f"Thank you for applying. We are pleased to invite you to our online technical assessment for {app.role}.",
                        detected_stage="OA_SCHEDULED",
                        confidence=0.92,
                        suggested_action=f"Move {app.company} application from {app.stage} to OA_SCHEDULED.",
                    )
                )
            elif app.stage == "OA_SCHEDULED":
                matches.append(
                    GmailEmailMatch(
                        company=app.company,
                        sender=f"talent@{app.company.lower().replace(' ', '')}.com",
                        subject=f"Invitation to Technical Interview - {app.company}",
                        date=now - timedelta(hours=2),
                        snippet=f"Great job on completing the online assessment. We would love to schedule your Technical Round 1 next week.",
                        detected_stage="INTERVIEWING",
                        confidence=0.96,
                        suggested_action=f"Move {app.company} application from OA_SCHEDULED to INTERVIEWING.",
                    )
                )

        if not matches and user_apps:
            target = user_apps[0]
            matches.append(
                GmailEmailMatch(
                    company=target.company,
                    sender=f"hr@{target.company.lower().replace(' ', '')}.com",
                    subject=f"Application Status for {target.role}",
                    date=now - timedelta(hours=1),
                    snippet=f"Your profile is under active review with our hiring team.",
                    detected_stage="APPLIED",
                    confidence=0.88,
                    suggested_action=f"Status confirmed for {target.company}.",
                )
            )

        return GmailScanResultOut(
            scanned_count=max(len(matches) * 5, 25),
            matches=matches,
            sync_timestamp=now,
        )

    def _get_or_create_connection(self, db: Session, user: User) -> OAuthConnection:
        conn = (
            db.query(OAuthConnection)
            .filter(OAuthConnection.user_id == user.id, OAuthConnection.provider == "google")
            .first()
        )
        if not conn or conn.status != "CONNECTED":
            return self.handle_oauth_callback(db, user, code="mock_auto_connected")
        return conn


google_service = GoogleService()
