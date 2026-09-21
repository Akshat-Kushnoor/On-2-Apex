import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from app.core.errors import AppException
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.job_match import JobMatch
from app.models.user import User
from app.schemas.job_analysis import JDAnalyzeRequest
from app.schemas.job_match import (
    JobMatchOut,
    MatchedSkillDetail,
    SmartSuggestion,
)
from app.services.jd_analyzer import jd_analyzer
from app.services.llm_gateway import llm_gateway
from app.services.skill_normalizer import get_canonical_skill_set, normalize_skill

SUGGESTION_SYSTEM_PROMPT = """You are a Principal Career Engineering Coach and Hiring Lead.
You analyze candidate profile gaps against a specific Job Description and provide high-impact, hyper-specific recommendations.
Rules:
1. When suggesting project enhancements, reference the candidate's ACTUAL project title.
2. Provide actionable technical instructions, not generic platitudes.
3. Return ONLY a strict JSON object with this exact structure:
{
  "improvement_explanation": "2-3 concise sentences diagnosing alignment and fastest route to eligibility.",
  "smart_suggestions": [
    {
      "type": "PROJECT_ENHANCEMENT",
      "title": "Clear action title referencing existing project",
      "action": "Specific implementation instructions",
      "impact": "Why this addresses JD requirements"
    },
    {
      "type": "DSA_PRACTICE",
      "title": "Targeted algorithmic focus",
      "action": "Specific data structures or patterns to practice",
      "impact": "Why this is critical for interview clearing"
    },
    {
      "type": "STACK_EXPANSION",
      "title": "Complementary library or tool addition",
      "action": "Specific library to learn within their current stack",
      "impact": "Closes a required technology gap"
    }
  ]
}"""


class SkillGapEngine:
    def compare_student_to_job(
        self,
        db: Session,
        user: User,
        job_id: str,
        force_recompute: bool = False,
    ) -> JobMatchOut:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise AppException(message="Job not found.", code="NOT_FOUND")

        if not force_recompute:
            cached_match = (
                db.query(JobMatch)
                .filter(JobMatch.user_id == user.id, JobMatch.job_id == job_id)
                .order_by(JobMatch.created_at.desc())
                .first()
            )
            if cached_match:
                return JobMatchOut.model_validate(cached_match)

        analysis = (
            db.query(JobAnalysis)
            .filter(JobAnalysis.job_id == job_id, JobAnalysis.user_id == user.id)
            .order_by(JobAnalysis.created_at.desc())
            .first()
        )
        if not analysis:
            analysis_out = jd_analyzer.analyze_job_description(
                db=db,
                user_id=user.id,
                request=JDAnalyzeRequest(job_id=job_id),
            )
            analysis = db.query(JobAnalysis).filter(JobAnalysis.id == analysis_out.id).first()

        matched_skills, missing_skills, score, breakdown = self._compute_deterministic_score(
            user=user,
            analysis=analysis,
        )

        improvement_explanation, smart_suggestions = self._generate_smart_llm_suggestions(
            db=db,
            user=user,
            job=job,
            analysis=analysis,
            missing_skills=missing_skills,
            score=score,
        )

        match_record = JobMatch(
            user_id=user.id,
            job_id=job.id,
            job_analysis_id=analysis.id if analysis else None,
            match_score=score,
            score_breakdown=breakdown,
            matched_skills=[m.model_dump() for m in matched_skills],
            missing_skills=missing_skills,
            improvement_explanation=improvement_explanation,
            smart_suggestions=[s.model_dump() for s in smart_suggestions],
            interview_topics=analysis.interview_topics if analysis else ["System Architecture", "Coding"],
        )
        db.add(match_record)
        db.commit()
        db.refresh(match_record)

        return JobMatchOut.model_validate(match_record)

    def _compute_deterministic_score(
        self,
        user: User,
        analysis: JobAnalysis,
    ) -> Tuple[List[MatchedSkillDetail], List[str], float, Dict[str, Any]]:
        candidate_evidence: Dict[str, Tuple[str, str]] = {}

        for skill in user.skills:
            norm = normalize_skill(skill.name)
            candidate_evidence[norm.lower()] = (skill.name, "Skills Section")

        for proj in user.projects:
            for tech in (proj.technologies or []):
                norm = normalize_skill(tech)
                if norm.lower() not in candidate_evidence:
                    candidate_evidence[norm.lower()] = (tech, f"Project: {proj.title}")

        for exp in user.experiences:
            for tech in (exp.technologies or []):
                norm = normalize_skill(tech)
                if norm.lower() not in candidate_evidence:
                    candidate_evidence[norm.lower()] = (tech, f"Experience: {exp.company}")

        required_skills = analysis.required_skills or []
        preferred_skills = analysis.preferred_skills or []

        matched_details: List[MatchedSkillDetail] = []
        missing_skills: List[str] = []

        req_matched_count = 0
        for req in required_skills:
            norm_req = normalize_skill(req)
            if norm_req.lower() in candidate_evidence:
                orig_name, source = candidate_evidence[norm_req.lower()]
                matched_details.append(
                    MatchedSkillDetail(
                        skill=req,
                        canonical_name=norm_req,
                        evidence_source=source,
                        source_type="Required",
                    )
                )
                req_matched_count += 1
            else:
                missing_skills.append(req)

        pref_matched_count = 0
        for pref in preferred_skills:
            norm_pref = normalize_skill(pref)
            if norm_pref.lower() in candidate_evidence:
                orig_name, source = candidate_evidence[norm_pref.lower()]
                matched_details.append(
                    MatchedSkillDetail(
                        skill=pref,
                        canonical_name=norm_pref,
                        evidence_source=source,
                        source_type="Preferred",
                    )
                )
                pref_matched_count += 1
            else:
                if pref not in missing_skills:
                    missing_skills.append(pref)

        req_ratio = (req_matched_count / len(required_skills)) if required_skills else 1.0
        pref_ratio = (pref_matched_count / len(preferred_skills)) if preferred_skills else 1.0

        project_score = 1.0 if len(user.projects) >= 2 else (0.5 if user.projects else 0.0)
        exp_score = 1.0 if user.experiences else 0.5
        edu_score = 1.0 if user.educations else 0.7

        total_score = (
            (req_ratio * 50.0) +
            (pref_ratio * 20.0) +
            (project_score * 15.0) +
            (exp_score * 10.0) +
            (edu_score * 5.0)
        )
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        breakdown = {
            "required_skills_pct": round(req_ratio * 100, 1),
            "preferred_skills_pct": round(pref_ratio * 100, 1),
            "project_evidence_score": round(project_score * 100, 1),
            "experience_score": round(exp_score * 100, 1),
            "education_score": round(edu_score * 100, 1),
            "weights": {
                "required_skills": 50,
                "preferred_skills": 20,
                "project_evidence": 15,
                "experience": 10,
                "education": 5,
            },
        }

        return matched_details, missing_skills, total_score, breakdown

    def _generate_smart_llm_suggestions(
        self,
        db: Session,
        user: User,
        job: Job,
        analysis: JobAnalysis,
        missing_skills: List[str],
        score: float,
    ) -> Tuple[str, List[SmartSuggestion]]:
        project_summaries = [
            f"'{p.title}' (Tech: {', '.join(p.technologies or [])})"
            for p in user.projects
        ]
        projects_str = "; ".join(project_summaries) if project_summaries else "No projects listed yet"

        skills_str = ", ".join([s.name for s in user.skills]) if user.skills else "No skills listed yet"
        missing_str = ", ".join(missing_skills[:6]) if missing_skills else "None"

        user_prompt = f"""Candidate Overview:
- Current Match Score: {score}%
- Existing Projects: {projects_str}
- Current Skills: {skills_str}

Target Role: {job.title} at {job.company}
Missing Skill Gaps: {missing_str}
Role Responsibilities: {', '.join((analysis.responsibilities or [])[:3])}

Provide strategic improvement recommendations tailored specifically to this candidate and role."""

        try:
            raw_response = llm_gateway.generate(
                prompt=user_prompt,
                system_prompt=SUGGESTION_SYSTEM_PROMPT,
                json_mode=True,
                user_id=user.id,
                db=db,
            )
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            data = json.loads(cleaned)

            explanation = data.get("improvement_explanation", f"Your alignment with {job.title} is {score}%. Target your missing skills to improve eligibility.")
            suggestions_data = data.get("smart_suggestions", [])

            suggestions = []
            for item in suggestions_data:
                stype = item.get("type", "STACK_EXPANSION")
                if stype not in {"PROJECT_ENHANCEMENT", "DSA_PRACTICE", "STACK_EXPANSION", "RESUME_OPTIMIZATION"}:
                    stype = "STACK_EXPANSION"
                suggestions.append(
                    SmartSuggestion(
                        type=stype,
                        title=item.get("title", "Skill Improvement"),
                        action=item.get("action", "Practice missing requirements."),
                        impact=item.get("impact", "Strengthens role readiness."),
                    )
                )

            if suggestions:
                return explanation, suggestions
        except Exception:
            pass

        first_project = user.projects[0].title if user.projects else "your primary project"
        primary_gap = missing_skills[0] if missing_skills else "Docker"

        fallback_explanation = f"You match {score}% of requirements for {job.title}. Closing the gaps in {', '.join(missing_skills[:3])} will significantly improve your profile."
        fallback_suggestions = [
            SmartSuggestion(
                type="PROJECT_ENHANCEMENT",
                title=f"Add {primary_gap} to '{first_project}'",
                action=f"Integrate {primary_gap} into '{first_project}' to directly demonstrate hands-on competence required by this JD.",
                impact=f"Provides tangible evidence for {primary_gap} on your resume.",
            ),
            SmartSuggestion(
                type="DSA_PRACTICE",
                title="Practice Core Data Structures & System Topics",
                action="Dedicate preparation to Graph traversals, Trees, and REST API architectural patterns.",
                impact="Ensures readiness for Round 1 technical problem-solving assessments.",
            ),
            SmartSuggestion(
                type="STACK_EXPANSION",
                title=f"Master {missing_skills[1] if len(missing_skills) > 1 else 'Cloud Fundamentals'}",
                action=f"Build a standalone prototype utilizing {missing_skills[1] if len(missing_skills) > 1 else 'AWS/GCP'} services.",
                impact="Eliminates an essential requirement bottleneck.",
            ),
        ]

        return fallback_explanation, fallback_suggestions


skill_gap_engine = SkillGapEngine()
