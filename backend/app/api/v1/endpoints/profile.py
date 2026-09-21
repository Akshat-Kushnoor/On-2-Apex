from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.db.session import get_db
from app.models.profile import (
    Achievement,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
    StudentProfile,
)
from app.models.user import User
from app.schemas.profile import (
    AchievementCreate,
    AchievementOut,
    CertificationCreate,
    CertificationOut,
    EducationCreate,
    EducationOut,
    ExperienceCreate,
    ExperienceOut,
    ExperienceUpdate,
    FullProfileOut,
    ProfileOut,
    ProfileUpdate,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    SkillCreate,
    SkillOut,
)

router = APIRouter()


# -------------------------------------------------------------
# Core Profile & Aggregated View
# -------------------------------------------------------------
@router.get("", response_model=FullProfileOut)
def get_full_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the complete student profile with aggregated skills, education, projects, etc."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return FullProfileOut(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        profile=ProfileOut.model_validate(profile),
        skills=[SkillOut.model_validate(s) for s in current_user.skills],
        educations=[EducationOut.model_validate(e) for e in current_user.educations],
        projects=[ProjectOut.model_validate(p) for p in current_user.projects],
        experiences=[ExperienceOut.model_validate(x) for x in current_user.experiences],
        certifications=[CertificationOut.model_validate(c) for c in current_user.certifications],
        achievements=[AchievementOut.model_validate(a) for a in current_user.achievements],
    )


@router.put("", response_model=ProfileOut)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates the student's base profile attributes."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


# -------------------------------------------------------------
# Skills Endpoints
# -------------------------------------------------------------
@router.get("/skills", response_model=List[SkillOut])
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all skills belonging to the authenticated student."""
    return db.query(Skill).filter(Skill.user_id == current_user.id).all()


@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def add_skill(
    skill_in: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a new skill to the authenticated student's profile."""
    skill = Skill(
        user_id=current_user.id,
        name=skill_in.name.strip(),
        category=skill_in.category,
        proficiency=skill_in.proficiency,
        evidence=skill_in.evidence,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_200_OK)
def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a skill verifying user ownership."""
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == current_user.id).first()
    if not skill:
        raise AppException(
            message="Skill not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(skill)
    db.commit()
    return {"status": "ok", "message": "Skill deleted successfully"}


# -------------------------------------------------------------
# Education Endpoints
# -------------------------------------------------------------
@router.get("/education", response_model=List[EducationOut])
def get_education(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all education records for the authenticated student."""
    return db.query(Education).filter(Education.user_id == current_user.id).all()


@router.post("/education", response_model=EducationOut, status_code=status.HTTP_201_CREATED)
def add_education(
    edu_in: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds an education record to the student's profile."""
    education = Education(
        user_id=current_user.id,
        institution=edu_in.institution.strip(),
        degree=edu_in.degree.strip(),
        branch=edu_in.branch.strip() if edu_in.branch else None,
        start_year=edu_in.start_year,
        end_year=edu_in.end_year,
        cgpa=edu_in.cgpa,
    )
    db.add(education)
    db.commit()
    db.refresh(education)
    return education


@router.delete("/education/{education_id}", status_code=status.HTTP_200_OK)
def delete_education(
    education_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes an education record verifying ownership."""
    education = db.query(Education).filter(Education.id == education_id, Education.user_id == current_user.id).first()
    if not education:
        raise AppException(
            message="Education record not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(education)
    db.commit()
    return {"status": "ok", "message": "Education record deleted successfully"}


# -------------------------------------------------------------
# Projects Endpoints
# -------------------------------------------------------------
@router.get("/projects", response_model=List[ProjectOut])
def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all projects for the authenticated student."""
    return db.query(Project).filter(Project.user_id == current_user.id).all()


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def add_project(
    proj_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a new project to the student's profile."""
    project = Project(
        user_id=current_user.id,
        title=proj_in.title.strip(),
        description=proj_in.description,
        technologies=proj_in.technologies,
        role=proj_in.role,
        repo_url=proj_in.repo_url,
        demo_url=proj_in.demo_url,
        achievements=proj_in.achievements,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    proj_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates an existing project verifying ownership."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise AppException(
            message="Project not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    update_data = proj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a project verifying ownership."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise AppException(
            message="Project not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(project)
    db.commit()
    return {"status": "ok", "message": "Project deleted successfully"}


# -------------------------------------------------------------
# Experience Endpoints
# -------------------------------------------------------------
@router.get("/experience", response_model=List[ExperienceOut])
def get_experience(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all work experience records for the authenticated student."""
    return db.query(Experience).filter(Experience.user_id == current_user.id).all()


@router.post("/experience", response_model=ExperienceOut, status_code=status.HTTP_201_CREATED)
def add_experience(
    exp_in: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a new experience record to the student's profile."""
    experience = Experience(
        user_id=current_user.id,
        company=exp_in.company.strip(),
        role=exp_in.role.strip(),
        start_date=exp_in.start_date,
        end_date=exp_in.end_date,
        description=exp_in.description,
        technologies=exp_in.technologies,
        achievements=exp_in.achievements,
    )
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience


@router.put("/experience/{experience_id}", response_model=ExperienceOut)
def update_experience(
    experience_id: str,
    exp_in: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates an existing experience record verifying ownership."""
    experience = db.query(Experience).filter(Experience.id == experience_id, Experience.user_id == current_user.id).first()
    if not experience:
        raise AppException(
            message="Experience record not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    update_data = exp_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experience, field, value)

    db.commit()
    db.refresh(experience)
    return experience


@router.delete("/experience/{experience_id}", status_code=status.HTTP_200_OK)
def delete_experience(
    experience_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes an experience record verifying ownership."""
    experience = db.query(Experience).filter(Experience.id == experience_id, Experience.user_id == current_user.id).first()
    if not experience:
        raise AppException(
            message="Experience record not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(experience)
    db.commit()
    return {"status": "ok", "message": "Experience record deleted successfully"}


# -------------------------------------------------------------
# Certifications Endpoints
# -------------------------------------------------------------
@router.get("/certifications", response_model=List[CertificationOut])
def get_certifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all certifications for the student."""
    return db.query(Certification).filter(Certification.user_id == current_user.id).all()


@router.post("/certifications", response_model=CertificationOut, status_code=status.HTTP_201_CREATED)
def add_certification(
    cert_in: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a certification to the student's profile."""
    certification = Certification(
        user_id=current_user.id,
        name=cert_in.name.strip(),
        issuing_organization=cert_in.issuing_organization,
        issue_date=cert_in.issue_date,
        credential_url=cert_in.credential_url,
    )
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification


@router.delete("/certifications/{cert_id}", status_code=status.HTTP_200_OK)
def delete_certification(
    cert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a certification verifying ownership."""
    certification = db.query(Certification).filter(Certification.id == cert_id, Certification.user_id == current_user.id).first()
    if not certification:
        raise AppException(
            message="Certification not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(certification)
    db.commit()
    return {"status": "ok", "message": "Certification deleted successfully"}


# -------------------------------------------------------------
# Achievements Endpoints
# -------------------------------------------------------------
@router.get("/achievements", response_model=List[AchievementOut])
def get_achievements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all achievements for the student."""
    return db.query(Achievement).filter(Achievement.user_id == current_user.id).all()


@router.post("/achievements", response_model=AchievementOut, status_code=status.HTTP_201_CREATED)
def add_achievement(
    ach_in: AchievementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds an achievement to the student's profile."""
    achievement = Achievement(
        user_id=current_user.id,
        title=ach_in.title.strip(),
        category=ach_in.category,
        date=ach_in.date,
        description=ach_in.description,
    )
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement


@router.delete("/achievements/{ach_id}", status_code=status.HTTP_200_OK)
def delete_achievement(
    ach_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes an achievement verifying ownership."""
    achievement = db.query(Achievement).filter(Achievement.id == ach_id, Achievement.user_id == current_user.id).first()
    if not achievement:
        raise AppException(
            message="Achievement not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(achievement)
    db.commit()
    return {"status": "ok", "message": "Achievement deleted successfully"}
