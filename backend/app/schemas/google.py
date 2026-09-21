from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GoogleAuthUrlOut(BaseModel):
    auth_url: str
    is_mock: bool = False


class GoogleConnectionStatusOut(BaseModel):
    connected: bool
    email: Optional[str] = None
    scopes: List[str] = []
    expires_at: Optional[datetime] = None
    is_mock: bool = False


class GoogleCalendarSyncResultOut(BaseModel):
    synced_events_count: int
    event_ids: List[str] = []
    calendar_summary: str


class TaskScheduleRequest(BaseModel):
    scheduled_time: Optional[datetime] = None
    duration_hours: float = Field(default=2.0, ge=0.5, le=8.0)


class GmailEmailMatch(BaseModel):
    company: str
    sender: str
    subject: str
    date: datetime
    snippet: str
    detected_stage: str
    confidence: float
    suggested_action: str


class GmailScanResultOut(BaseModel):
    scanned_count: int
    matches: List[GmailEmailMatch] = []
    sync_timestamp: datetime
