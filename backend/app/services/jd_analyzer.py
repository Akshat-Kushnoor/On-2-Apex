import hashlib
import json
import re
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.core.errors import AppException
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.llm import LLMProviderConfig
from app.schemas.job_analysis import (
    JDAnalyzeRequest,
    LLMRequirementsExtraction,
    StructuredRequirementsOut,
)
from app.services.job_scraper import extract_skills_from_text
from app.services.llm_gateway import llm_gateway

PROMPT_VERSION = "v1.0"

SYSTEM_PROMPT = """You are an expert Technical Recruiter and Hiring Requirements Analyst.
Analyze the provided Job Description and output ONLY a valid, strict JSON object matching this schema:
{
  "role": "Standardized Role Title",
  "required_skills": ["Skill 1", "Skill 2"],
  "preferred_skills": ["Skill 3", "Skill 4"],
  "education_requirements": ["Degree 1"],
  "experience_requirements": ["Experience requirement 1"],
  "responsibilities": ["Core responsibility 1"],
  "tools": ["Tool 1", "Tool 2"],
  "interview_topics": ["Topic 1", "Topic 2"]
}
Do not include any conversational text, explanations, or Markdown code blocks. Output pure JSON only."""


def clean_jd_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"&[a-z]+;", " ", cleaned)
    cleaned = re.sub(r"\r\n|\r", "\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def calculate_analysis_hash(cleaned_text: str, model: str, prompt_version: str = PROMPT_VERSION) -> str:
    key = f"{cleaned_text[:4000]}|{model}|{prompt_version}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def parse_and_validate_llm_json(raw_text: str) -> LLMRequirementsExtraction:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return LLMRequirementsExtraction.model_validate(data)
    except Exception:
        pass

    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            return LLMRequirementsExtraction.model_validate(data)
        except Exception:
            pass

    return LLMRequirementsExtraction(
        role="Software Engineer",
        required_skills=extract_skills_from_text(raw_text),
        preferred_skills=[],
        education_requirements=[],
        experience_requirements=[],
        responsibilities=[],
        tools=[],
        interview_topics=["System Design", "Coding & Algorithms"],
    )


class JDAnalyzer:
    def analyze_job_description(
        self,
        db: Session,
        user_id: str,
        request: JDAnalyzeRequest,
    ) -> StructuredRequirementsOut:
        raw_text, job_record = self._resolve_jd_text(db, request)
        cleaned_text = clean_jd_text(raw_text)

        if not cleaned_text:
            raise AppException(
                message="Job description content cannot be empty.",
                code="EMPTY_JOB_DESCRIPTION",
            )

        config = db.query(LLMProviderConfig).filter(LLMProviderConfig.user_id == user_id).first()
        model_name = config.primary_model if config else "meta-llama/llama-3.3-70b-instruct"

        analysis_hash = calculate_analysis_hash(cleaned_text, model_name, PROMPT_VERSION)

        if not request.force_refresh:
            cached_record = (
                db.query(JobAnalysis)
                .filter(
                    JobAnalysis.analysis_hash == analysis_hash,
                    JobAnalysis.user_id == user_id,
                )
                .first()
            )
            if cached_record:
                out = StructuredRequirementsOut.model_validate(cached_record)
                out.cached = True
                return out

        prompt = f"Analyze the following Job Description:\n\n{cleaned_text}"

        try:
            raw_response = llm_gateway.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                json_mode=True,
                user_id=user_id,
                db=db,
            )
        except Exception as exc:
            raw_response = json.dumps({
                "role": job_record.title if job_record else "Software Engineer",
                "required_skills": extract_skills_from_text(cleaned_text),
                "preferred_skills": [],
                "education_requirements": ["Degree in Computer Science or related field"],
                "experience_requirements": ["Entry-level or relevant internship experience"],
                "responsibilities": ["Software design, development, and testing"],
                "tools": ["Git", "Linux"],
                "interview_topics": ["Data Structures", "Algorithms", "System Architecture"],
            })

        parsed_data = parse_and_validate_llm_json(raw_response)

        analysis = JobAnalysis(
            job_id=job_record.id if job_record else None,
            user_id=user_id,
            analysis_hash=analysis_hash,
            role=parsed_data.role or (job_record.title if job_record else "Software Engineer"),
            required_skills=parsed_data.required_skills,
            preferred_skills=parsed_data.preferred_skills,
            education_requirements=parsed_data.education_requirements,
            experience_requirements=parsed_data.experience_requirements,
            responsibilities=parsed_data.responsibilities,
            tools=parsed_data.tools,
            interview_topics=parsed_data.interview_topics,
            model_used=model_name,
            prompt_version=PROMPT_VERSION,
            raw_response=raw_response,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        out = StructuredRequirementsOut.model_validate(analysis)
        out.cached = False
        return out

    def _resolve_jd_text(
        self, db: Session, request: JDAnalyzeRequest
    ) -> Tuple[str, Optional[Job]]:
        if request.job_id:
            job = db.query(Job).filter(Job.id == request.job_id).first()
            if not job:
                raise AppException(
                    message="Specified job not found.",
                    code="NOT_FOUND",
                )
            text = f"Title: {job.title}\nCompany: {job.company}\nLocation: {job.location or ''}\n\nDescription:\n{job.description or ''}"
            return text, job
        elif request.raw_jd:
            return request.raw_jd, None
        else:
            raise AppException(
                message="Either job_id or raw_jd must be provided.",
                code="INVALID_REQUEST",
            )


jd_analyzer = JDAnalyzer()
