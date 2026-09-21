from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.errors import AppException
from app.models.application import Application, ApplicationEvent
from app.models.job import Job
from app.models.resume import GeneratedResume
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

CANONICAL_STAGES = [
    "WISHLIST",
    "APPLIED",
    "OA_SCHEDULED",
    "INTERVIEWING",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]


class WorkspaceService:
    def create_application(
        self,
        db: Session,
        user: User,
        payload: ApplicationCreateRequest,
    ) -> ApplicationOut:
        if payload.job_id:
            job = db.query(Job).filter(Job.id == payload.job_id).first()
            if not job:
                raise AppException(message="Job not found.", code="NOT_FOUND", status_code=404)

        if payload.resume_id:
            resume = (
                db.query(GeneratedResume)
                .filter(GeneratedResume.id == payload.resume_id, GeneratedResume.user_id == user.id)
                .first()
            )
            if not resume:
                raise AppException(message="Resume not found.", code="NOT_FOUND", status_code=404)

            company_name = payload.company.strip()
            current_companies = list(resume.applied_companies or [])
            if company_name and company_name not in current_companies:
                current_companies.append(company_name)
                resume.applied_companies = current_companies

        applied_timestamp = payload.applied_at
        if payload.stage == "APPLIED" and not applied_timestamp:
            applied_timestamp = datetime.now(timezone.utc)

        app_record = Application(
            user_id=user.id,
            job_id=payload.job_id,
            resume_id=payload.resume_id,
            company=payload.company.strip(),
            role=payload.role.strip(),
            stage=payload.stage,
            job_url=payload.job_url.strip() if payload.job_url else None,
            salary=payload.salary.strip() if payload.salary else None,
            location=payload.location.strip() if payload.location else None,
            notes=payload.notes.strip() if payload.notes else None,
            deadline=payload.deadline,
            applied_at=applied_timestamp,
        )
        db.add(app_record)
        db.flush()

        initial_event = ApplicationEvent(
            application_id=app_record.id,
            user_id=user.id,
            event_type="STAGE_CHANGE",
            title=f"Application created in {payload.stage}",
            description=f"Initial record created for {app_record.role} at {app_record.company}.",
            event_date=applied_timestamp or datetime.now(timezone.utc),
        )
        db.add(initial_event)
        db.commit()
        db.refresh(app_record)

        return ApplicationOut.model_validate(app_record)

    def get_board(self, db: Session, user: User) -> WorkspaceBoardOut:
        apps = (
            db.query(Application)
            .filter(Application.user_id == user.id)
            .order_by(Application.created_at.desc())
            .all()
        )

        stages_dict = {s.lower(): [] for s in CANONICAL_STAGES}
        for app in apps:
            stage_key = app.stage.lower() if app.stage.lower() in stages_dict else "wishlist"
            brief = ApplicationBrief(
                id=app.id,
                company=app.company,
                role=app.role,
                stage=app.stage,
                job_id=app.job_id,
                resume_id=app.resume_id,
                salary=app.salary,
                location=app.location,
                deadline=app.deadline,
                applied_at=app.applied_at,
                events_count=len(app.events or []),
                created_at=app.created_at,
            )
            stages_dict[stage_key].append(brief)

        return WorkspaceBoardOut(
            total_applications=len(apps),
            stages=stages_dict,
        )

    def list_applications(
        self,
        db: Session,
        user: User,
        stage: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ApplicationBrief]:
        query = db.query(Application).filter(Application.user_id == user.id)

        if stage:
            query = query.filter(Application.stage == stage.upper())
        if company:
            query = query.filter(Application.company.ilike(f"%{company.strip()}%"))
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(or_(Application.company.ilike(term), Application.role.ilike(term)))

        apps = query.order_by(Application.created_at.desc()).all()
        return [
            ApplicationBrief(
                id=a.id,
                company=a.company,
                role=a.role,
                stage=a.stage,
                job_id=a.job_id,
                resume_id=a.resume_id,
                salary=a.salary,
                location=a.location,
                deadline=a.deadline,
                applied_at=a.applied_at,
                events_count=len(a.events or []),
                created_at=a.created_at,
            )
            for a in apps
        ]

    def get_application_detail(
        self,
        db: Session,
        user: User,
        application_id: str,
    ) -> ApplicationOut:
        app_record = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app_record:
            raise AppException(message="Application not found.", code="NOT_FOUND", status_code=404)
        return ApplicationOut.model_validate(app_record)

    def update_application(
        self,
        db: Session,
        user: User,
        application_id: str,
        payload: ApplicationUpdateRequest,
    ) -> ApplicationOut:
        app_record = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app_record:
            raise AppException(message="Application not found.", code="NOT_FOUND", status_code=404)

        if payload.company is not None:
            app_record.company = payload.company.strip()
        if payload.role is not None:
            app_record.role = payload.role.strip()
        if payload.job_id is not None:
            app_record.job_id = payload.job_id
        if payload.resume_id is not None:
            app_record.resume_id = payload.resume_id
        if payload.job_url is not None:
            app_record.job_url = payload.job_url.strip() or None
        if payload.salary is not None:
            app_record.salary = payload.salary.strip() or None
        if payload.location is not None:
            app_record.location = payload.location.strip() or None
        if payload.notes is not None:
            app_record.notes = payload.notes.strip() or None
        if payload.deadline is not None:
            app_record.deadline = payload.deadline
        if payload.applied_at is not None:
            app_record.applied_at = payload.applied_at

        db.commit()
        db.refresh(app_record)
        return ApplicationOut.model_validate(app_record)

    def update_stage(
        self,
        db: Session,
        user: User,
        application_id: str,
        payload: ApplicationStageUpdateRequest,
    ) -> ApplicationOut:
        app_record = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app_record:
            raise AppException(message="Application not found.", code="NOT_FOUND", status_code=404)

        old_stage = app_record.stage
        new_stage = payload.stage

        if old_stage != new_stage:
            app_record.stage = new_stage
            if new_stage == "APPLIED" and not app_record.applied_at:
                app_record.applied_at = datetime.now(timezone.utc)

            event = ApplicationEvent(
                application_id=app_record.id,
                user_id=user.id,
                event_type="STAGE_CHANGE",
                title=f"Stage changed: {old_stage} -> {new_stage}",
                description=payload.note or f"Moved status from {old_stage} to {new_stage}.",
                event_date=datetime.now(timezone.utc),
            )
            db.add(event)
            db.commit()
            db.refresh(app_record)

        return ApplicationOut.model_validate(app_record)

    def add_event(
        self,
        db: Session,
        user: User,
        application_id: str,
        payload: ApplicationEventCreateRequest,
    ) -> ApplicationEventOut:
        app_record = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app_record:
            raise AppException(message="Application not found.", code="NOT_FOUND", status_code=404)

        event = ApplicationEvent(
            application_id=app_record.id,
            user_id=user.id,
            event_type=payload.event_type,
            title=payload.title.strip(),
            description=payload.description.strip() if payload.description else None,
            event_date=payload.event_date or datetime.now(timezone.utc),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return ApplicationEventOut.model_validate(event)

    def get_upcoming(
        self,
        db: Session,
        user: User,
        days_ahead: int = 14,
    ) -> List[UpcomingDeadlineOut]:
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=days_ahead)

        apps_with_deadlines = (
            db.query(Application)
            .filter(
                Application.user_id == user.id,
                Application.deadline.isnot(None),
                Application.deadline >= now - timedelta(days=1),
                Application.deadline <= horizon,
            )
            .all()
        )

        upcoming_events = (
            db.query(ApplicationEvent)
            .join(Application, ApplicationEvent.application_id == Application.id)
            .filter(
                ApplicationEvent.user_id == user.id,
                ApplicationEvent.event_date >= now - timedelta(days=1),
                ApplicationEvent.event_date <= horizon,
                ApplicationEvent.event_type.in_(["INTERVIEW_SCHEDULED", "OA_DEADLINE"]),
            )
            .all()
        )

        results = []
        for a in apps_with_deadlines:
            results.append(
                UpcomingDeadlineOut(
                    application_id=a.id,
                    company=a.company,
                    role=a.role,
                    stage=a.stage,
                    title=f"Application Deadline: {a.company}",
                    deadline_date=a.deadline,
                    event_type="APPLICATION_DEADLINE",
                )
            )

        for ev in upcoming_events:
            app = ev.application
            results.append(
                UpcomingDeadlineOut(
                    application_id=app.id,
                    company=app.company,
                    role=app.role,
                    stage=app.stage,
                    title=ev.title,
                    deadline_date=ev.event_date,
                    event_type=ev.event_type,
                )
            )

        results.sort(key=lambda x: x.deadline_date)
        return results

    def delete_application(
        self,
        db: Session,
        user: User,
        application_id: str,
    ) -> None:
        app_record = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id)
            .first()
        )
        if not app_record:
            raise AppException(message="Application not found.", code="NOT_FOUND", status_code=404)
        db.delete(app_record)
        db.commit()


workspace_service = WorkspaceService()
