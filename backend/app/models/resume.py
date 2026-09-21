import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base import TimestampMixin


class GeneratedResume(Base, TimestampMixin):
    __tablename__ = "generated_resumes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    applied_companies: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    markdown: Mapped[str] = mapped_column(Text, nullable=False)
    latex: Mapped[str] = mapped_column(Text, nullable=False)
    diffs: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False)

    user: Mapped["User"] = relationship("User")
    job: Mapped[Optional["Job"]] = relationship("Job")
