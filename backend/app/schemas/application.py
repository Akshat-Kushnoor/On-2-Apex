from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

ApplicationStage = Literal[
    "WISHLIST",
    "APPLIED",
    "OA_SCHEDULED",
    "INTERVIEWING",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]

ApplicationEventType = Literal[
    "STAGE_CHANGE",
    "NOTE_ADDED",
    "INTERVIEW_SCHEDULED",
    "OA_DEADLINE",
    "OFFER_RECEIVED",
    "REJECTION_RECEIVED",
    "STATUS_UPDATE",
]


class ApplicationCreateRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    job_id: Optional[str] = None
    resume_id: Optional[str] = None
    stage: ApplicationStage = "WISHLIST"
    job_url: Optional[str] = Field(default=None, max_length=500)
    salary: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    deadline: Optional[datetime] = None
    applied_at: Optional[datetime] = None


class ApplicationUpdateRequest(BaseModel):
    company: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, max_length=255)
    job_id: Optional[str] = None
    resume_id: Optional[str] = None
    job_url: Optional[str] = Field(default=None, max_length=500)
    salary: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    deadline: Optional[datetime] = None
    applied_at: Optional[datetime] = None


class ApplicationStageUpdateRequest(BaseModel):
    stage: ApplicationStage
    note: Optional[str] = Field(default=None, max_length=500)


class ApplicationEventCreateRequest(BaseModel):
    event_type: ApplicationEventType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: Optional[datetime] = None


class ApplicationEventOut(BaseModel):
    id: str
    application_id: str
    user_id: str
    event_type: str
    title: str
    description: Optional[str] = None
    event_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationBrief(BaseModel):
    id: str
    company: str
    role: str
    stage: str
    job_id: Optional[str] = None
    resume_id: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    events_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationOut(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    resume_id: Optional[str] = None
    company: str
    role: str
    stage: str
    job_url: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    deadline: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    events: List[ApplicationEventOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceBoardOut(BaseModel):
    total_applications: int
    stages: Dict[str, List[ApplicationBrief]]


class UpcomingDeadlineOut(BaseModel):
    application_id: str
    company: str
    role: str
    stage: str
    title: str
    deadline_date: datetime
    event_type: str
