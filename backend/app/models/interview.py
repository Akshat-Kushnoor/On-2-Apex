import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import ForeignKey, JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base import TimestampMixin


class InterviewSession(Base, TimestampMixin):
    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    verdict: Mapped[str] = mapped_column(String(50), nullable=False, default="NEEDS WORK")
    param_scores: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    questions_and_answers: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    strengths: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    improvements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped["User"] = relationship("User")
