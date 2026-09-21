from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

SuggestionType = Literal["PROJECT_ENHANCEMENT", "DSA_PRACTICE", "STACK_EXPANSION", "RESUME_OPTIMIZATION"]


class SmartSuggestion(BaseModel):
    type: SuggestionType
    title: str
    action: str
    impact: str


class MatchedSkillDetail(BaseModel):
    skill: str
    canonical_name: str
    evidence_source: str
    source_type: str


class JobMatchRequest(BaseModel):
    force_recompute: bool = False


class JobMatchOut(BaseModel):
    id: str
    user_id: str
    job_id: str
    job_analysis_id: Optional[str] = None
    match_score: float
    score_breakdown: Dict[str, Any]
    matched_skills: List[MatchedSkillDetail]
    missing_skills: List[str]
    improvement_explanation: str
    smart_suggestions: List[SmartSuggestion]
    interview_topics: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
