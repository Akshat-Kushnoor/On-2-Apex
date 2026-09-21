from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobOut, JobSearchQuery, JobSearchResult
from app.services.job_normalizer import (
    calculate_dedup_hash,
    canonicalize_url,
    normalize_company,
    normalize_title,
)

COMMON_SKILL_KEYWORDS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
    "Django", "Flask", "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker",
    "Kubernetes", "AWS", "Azure", "GCP", "Git", "CI/CD", "Linux",
    "REST", "GraphQL", "Java", "C++", "C#", "Go", "Rust", "HTML", "CSS",
    "Tailwind", "Next.js", "Express", "Microservices", "Data Structures",
    "Algorithms", "Machine Learning", "PyTorch", "TensorFlow",
]


@dataclass
class RawJob:
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: str = "unknown"
    posted_at: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None


def extract_skills_from_text(text: str) -> List[str]:
    if not text:
        return []
    found = []
    for skill in COMMON_SKILL_KEYWORDS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return found


class BaseJobSource(ABC):
    @abstractmethod
    def search(self, query: JobSearchQuery) -> Tuple[List[RawJob], Dict[str, str]]:
        pass


class JobSpySource(BaseJobSource):
    def search(self, query: JobSearchQuery) -> Tuple[List[RawJob], Dict[str, str]]:
        raw_jobs: List[RawJob] = []
        statuses: Dict[str, str] = {}
        sites = ["indeed", "linkedin", "glassdoor", "zip_recruiter"]

        try:
            from jobspy import scrape_jobs

            search_term = query.role
            if query.keywords:
                search_term = f"{query.role} {' '.join(query.keywords[:3])}"

            country = "india" if "india" in (query.location or "").lower() or "bengaluru" in (query.location or "").lower() or "bangalore" in (query.location or "").lower() else "usa"

            results_df = scrape_jobs(
                site_name=sites,
                search_term=search_term,
                location=query.location or "",
                results_wanted=query.limit,
                country_indeed=country,
            )

            if results_df is not None and not results_df.empty:
                for _, row in results_df.iterrows():
                    title = str(row.get("title") or "")
                    company = str(row.get("company") or "")
                    if not title or not company or company.lower() == "nan":
                        continue

                    location = str(row.get("location") or "") if row.get("location") else None
                    desc = str(row.get("description") or "") if row.get("description") else None
                    url = str(row.get("job_url") or "") if row.get("job_url") else None
                    site = str(row.get("site") or "jobspy")

                    min_amt = row.get("min_amount")
                    max_amt = row.get("max_amount")
                    curr = row.get("currency")

                    raw_jobs.append(
                        RawJob(
                            title=title,
                            company=company,
                            location=location if location != "nan" else None,
                            description=desc if desc != "nan" else None,
                            url=url if url != "nan" else None,
                            source=site,
                            posted_at=str(row.get("date_posted")) if row.get("date_posted") else None,
                            experience_level=query.experience,
                            salary_min=float(min_amt) if min_amt and str(min_amt) != "nan" else None,
                            salary_max=float(max_amt) if max_amt and str(max_amt) != "nan" else None,
                            currency=str(curr) if curr and str(curr) != "nan" else None,
                        )
                    )

                for site in sites:
                    statuses[site] = "completed"
            else:
                for site in sites:
                    statuses[site] = "no_results"

        except Exception as exc:
            for site in sites:
                statuses[site] = f"failed: {str(exc)[:100]}"

        return raw_jobs, statuses


class FallbackSampleSource(BaseJobSource):
    def search(self, query: JobSearchQuery) -> Tuple[List[RawJob], Dict[str, str]]:
        role = query.role.strip()
        loc = query.location or "Bengaluru, India"
        sample_data = [
            RawJob(
                title=f"Junior {role}",
                company="Apex Innovations",
                location=loc,
                description=f"We are hiring a passionate Junior {role} to work on backend microservices and modern interfaces. Requirements: Python, FastAPI, React, SQL, and Docker.",
                url="https://jobs.apex-innovations.io/apply/101",
                source="direct_board",
                experience_level="entry_level",
                salary_min=600000.0,
                salary_max=900000.0,
                currency="INR",
            ),
            RawJob(
                title=f"{role} (Placement Opportunity)",
                company="CloudScale Systems",
                location=loc,
                description=f"CloudScale Systems is looking for a {role}. Must have strong problem solving skills, Data Structures, Algorithms, REST APIs, Git, and cloud fundamentals.",
                url="https://cloudscale.com/careers/freshers",
                source="direct_board",
                experience_level="entry_level",
                salary_min=800000.0,
                salary_max=1200000.0,
                currency="INR",
            ),
            RawJob(
                title=f"Graduate Engineer Trainee - {role}",
                company="NextGen Tech Solutions",
                location=loc,
                description=f"Exciting trainee role for freshers. You will build and test distributed services using Python, TypeScript, PostgreSQL, and Linux.",
                url="https://nextgen.dev/careers/graduate-engineer",
                source="direct_board",
                experience_level="entry_level",
                salary_min=700000.0,
                salary_max=1000000.0,
                currency="INR",
            ),
        ]
        return sample_data, {"fallback_board": "completed"}


class JobService:
    def __init__(self):
        self.jobspy_source = JobSpySource()
        self.fallback_source = FallbackSampleSource()

    def search_and_ingest(
        self, db: Session, query: JobSearchQuery
    ) -> JobSearchResult:
        raw_jobs, statuses = self.jobspy_source.search(query)

        if not raw_jobs:
            fallback_jobs, fallback_statuses = self.fallback_source.search(query)
            raw_jobs.extend(fallback_jobs)
            statuses.update(fallback_statuses)

        new_count = 0
        persisted_jobs: List[Job] = []

        for item in raw_jobs:
            norm_comp = normalize_company(item.company)
            norm_tit = normalize_title(item.title)
            can_url = canonicalize_url(item.url)
            dedup_hash = calculate_dedup_hash(
                norm_comp, norm_tit, can_url, item.location
            )

            existing = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()
            if existing:
                persisted_jobs.append(existing)
                continue

            extracted_skills = extract_skills_from_text(
                f"{item.title} {item.description or ''}"
            )

            new_job = Job(
                title=item.title,
                company=item.company,
                normalized_company=norm_comp,
                normalized_title=norm_tit,
                location=item.location,
                description=item.description,
                url=item.url,
                canonical_url=can_url,
                dedup_hash=dedup_hash,
                source=item.source,
                posted_at=item.posted_at,
                experience_level=item.experience_level,
                skills=extracted_skills,
                salary_min=item.salary_min,
                salary_max=item.salary_max,
                currency=item.currency,
                is_active=True,
            )
            db.add(new_job)
            persisted_jobs.append(new_job)
            new_count += 1

        db.commit()
        for j in persisted_jobs:
            db.refresh(j)

        return JobSearchResult(
            total_found=len(persisted_jobs),
            new_added=new_count,
            sources_status=statuses,
            jobs=[JobOut.model_validate(j) for j in persisted_jobs],
        )


job_service = JobService()
