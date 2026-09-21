from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class JDAnalyzeRequest(BaseModel):
    job_id: Optional[str] = None
    raw_jd: Optional[str] = Field(default=None, max_length=50000)
    force_refresh: bool = False


class LLMRequirementsExtraction(BaseModel):
    role: str = Field(default="Software Engineer")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    experience_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    interview_topics: List[str] = Field(default_factory=list)


class StructuredRequirementsOut(BaseModel):
    id: str
    job_id: Optional[str] = None
    role: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_requirements: List[str] = []
    experience_requirements: List[str] = []
    responsibilities: List[str] = []
    tools: List[str] = []
    interview_topics: List[str] = []
    model_used: str
    prompt_version: str
    cached: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
