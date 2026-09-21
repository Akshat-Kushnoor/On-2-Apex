import uuid
from datetime import datetime
from typing import Any, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base import TimestampMixin


class LearningPlan(Base, TimestampMixin):
    __tablename__ = "learning_plans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    job_match_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("job_matches.id", ondelete="SET NULL"), nullable=True
    )
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    target_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hours_per_week: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    total_weeks: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    total_estimated_hours: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)

    tasks: Mapped[List["LearningTask"]] = relationship(
        "LearningTask", back_populates="plan", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User")
    job: Mapped[Optional["Job"]] = relationship("Job")


class LearningTask(Base, TimestampMixin):
    __tablename__ = "learning_tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("learning_plans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    estimated_hours: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="NOT_STARTED", nullable=False)
    learning_goal: Mapped[str] = mapped_column(Text, nullable=False)
    topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    practice_project: Mapped[str] = mapped_column(Text, nullable=False)
    interview_question_prep: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    plan: Mapped["LearningPlan"] = relationship("LearningPlan", back_populates="tasks")
    user: Mapped["User"] = relationship("User")
