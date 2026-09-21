from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# -------------------------------------------------------------
# Base Profile Schemas
# -------------------------------------------------------------
class ProfileUpdate(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    work_authorization: Optional[str] = None
    bio: Optional[str] = None


class ProfileOut(BaseModel):
    id: str
    user_id: str
    phone: Optional[str] = None
    location: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    work_authorization: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Skill Schemas
# -------------------------------------------------------------
class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(default="General", max_length=100)
    proficiency: Optional[str] = Field(default="Intermediate", max_length=50)
    evidence: Optional[str] = None


class SkillOut(BaseModel):
    id: str
    user_id: str
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    evidence: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Education Schemas
# -------------------------------------------------------------
class EducationCreate(BaseModel):
    institution: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., min_length=1, max_length=100)
    branch: Optional[str] = Field(default=None, max_length=100)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    cgpa: Optional[str] = Field(default=None, max_length=50)


class EducationOut(BaseModel):
    id: str
    user_id: str
    institution: str
    degree: str
    branch: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    cgpa: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Project Schemas
# -------------------------------------------------------------
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    technologies: List[str] = []
    role: Optional[str] = None
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    achievements: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    role: Optional[str] = None
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    achievements: Optional[str] = None


class ProjectOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    technologies: List[str] = []
    role: Optional[str] = None
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    achievements: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Experience Schemas
# -------------------------------------------------------------
class ExperienceCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []
    achievements: Optional[str] = None


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[str] = None


class ExperienceOut(BaseModel):
    id: str
    user_id: str
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []
    achievements: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Certification Schemas
# -------------------------------------------------------------
class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationOut(BaseModel):
    id: str
    user_id: str
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Achievement Schemas
# -------------------------------------------------------------
class AchievementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(default="General", max_length=100)
    date: Optional[str] = None
    description: Optional[str] = None


class AchievementOut(BaseModel):
    id: str
    user_id: str
    title: str
    category: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Aggregated Full Profile Schema
# -------------------------------------------------------------
class FullProfileOut(BaseModel):
    user_id: str
    email: str
    full_name: str
    profile: Optional[ProfileOut] = None
    skills: List[SkillOut] = []
    educations: List[EducationOut] = []
    projects: List[ProjectOut] = []
    experiences: List[ExperienceOut] = []
    certifications: List[CertificationOut] = []
    achievements: List[AchievementOut] = []
