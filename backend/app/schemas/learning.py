from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

TaskStatusType = Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "VERIFIED"]


class LearningPlanCreateRequest(BaseModel):
    job_id: str
    hours_per_week: int = Field(default=10, ge=2, le=50)
    target_weeks: int = Field(default=4, ge=1, le=16)


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatusType
    evidence: Optional[str] = Field(default=None, max_length=1000)


class LearningTaskOut(BaseModel):
    id: str
    plan_id: str
    user_id: str
    skill: str
    title: str
    description: str
    week_number: int
    priority: str
    estimated_hours: float
    status: str
    learning_goal: str
    topics: List[str] = []
    practice_project: str
    interview_question_prep: str
    evidence: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningPlanOut(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    target_role: str
    target_company: Optional[str] = None
    hours_per_week: int
    total_weeks: int
    total_estimated_hours: float
    status: str
    progress_pct: float
    completed_hours: float
    tasks: List[LearningTaskOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
