from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestionItem(BaseModel):
    id: int
    category: str
    title: str
    question: str
    hint: Optional[str] = None


class InterviewStartRequest(BaseModel):
    position: str = Field(..., min_length=1, max_length=255)


class InterviewStartResponse(BaseModel):
    position: str
    questions: List[InterviewQuestionItem]


class InterviewAnswerItem(BaseModel):
    question_id: int
    category: str
    question: str
    answer: str


class InterviewEvaluateRequest(BaseModel):
    position: str
    answers: List[InterviewAnswerItem]


class InterviewScorecardOut(BaseModel):
    id: str
    position: str
    overall_score: int = Field(..., ge=0, le=100)
    verdict: str
    param_scores: Dict[str, int]
    questions_and_answers: List[Dict[str, Any]]
    strengths: List[str]
    improvements: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionBrief(BaseModel):
    id: str
    position: str
    overall_score: int
    verdict: str
    param_scores: Dict[str, int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
