import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base import TimestampMixin


class JobAnalysis(Base, TimestampMixin):
    __tablename__ = "job_analyses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    analysis_hash: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    required_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    education_requirements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    experience_requirements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    responsibilities: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    tools: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    interview_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), default="unknown", nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    job: Mapped[Optional["Job"]] = relationship("Job")
    user: Mapped["User"] = relationship("User")
