import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base import TimestampMixin


class JobMatch(Base, TimestampMixin):
    __tablename__ = "job_matches"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_analysis_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("job_analyses.id", ondelete="SET NULL"), nullable=True
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    matched_skills: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    improvement_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    smart_suggestions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    interview_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped["User"] = relationship("User")
    job: Mapped["Job"] = relationship("Job")
    job_analysis: Mapped[Optional["JobAnalysis"]] = relationship("JobAnalysis")
