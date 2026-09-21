import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.errors import AppException
from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.learning import LearningPlan, LearningTask
from app.models.user import User
from app.schemas.learning import (
    LearningPlanCreateRequest,
    LearningPlanOut,
    LearningTaskOut,
)
from app.services.llm_gateway import llm_gateway
from app.services.skill_gap_engine import skill_gap_engine

PLAN_SYSTEM_PROMPT = """You are a Principal Curriculum Architect and Technical Career Coach.
Generate a structured, weekly learning roadmap for a student addressing their skill gaps for a target job.
Constraint: Respect the weekly hours limit strictly.
Return ONLY a valid JSON object matching this schema:
{
  "tasks": [
    {
      "skill": "Skill Name",
      "title": "Clear actionable task title",
      "description": "What to learn and why",
      "week_number": 1,
      "priority": "HIGH",
      "estimated_hours": 3.0,
      "learning_goal": "Clear measurable learning objective",
      "topics": ["Topic 1", "Topic 2", "Topic 3"],
      "practice_project": "Hands-on implementation task referencing candidate project",
      "interview_question_prep": "Key questions and concepts tested in interviews"
    }
  ]
}"""


class LearningEngine:
    def create_learning_plan(
        self,
        db: Session,
        user: User,
        request: LearningPlanCreateRequest,
    ) -> LearningPlanOut:
        job = db.query(Job).filter(Job.id == request.job_id).first()
        if not job:
            raise AppException(message="Job not found.", code="NOT_FOUND", status_code=404)

        match_record = (
            db.query(JobMatch)
            .filter(JobMatch.user_id == user.id, JobMatch.job_id == job.id)
            .order_by(JobMatch.created_at.desc())
            .first()
        )
        if not match_record:
            match_out = skill_gap_engine.compare_student_to_job(db=db, user=user, job_id=job.id)
            match_record = db.query(JobMatch).filter(JobMatch.id == match_out.id).first()

        existing_plans = (
            db.query(LearningPlan)
            .filter(LearningPlan.user_id == user.id, LearningPlan.job_id == job.id, LearningPlan.status == "ACTIVE")
            .all()
        )
        for p in existing_plans:
            p.status = "ARCHIVED"

        missing_skills = match_record.missing_skills or ["Docker", "System Design", "Cloud Infrastructure"]
        project_names = [p.title for p in user.projects] if user.projects else ["Portfolio Application"]
        primary_project = project_names[0]

        generated_tasks = self._generate_tasks(
            db=db,
            user=user,
            job=job,
            missing_skills=missing_skills,
            hours_per_week=request.hours_per_week,
            target_weeks=request.target_weeks,
            primary_project=primary_project,
        )

        total_hours = sum(t["estimated_hours"] for t in generated_tasks)

        plan = LearningPlan(
            user_id=user.id,
            job_id=job.id,
            job_match_id=match_record.id,
            target_role=job.title,
            target_company=job.company,
            hours_per_week=request.hours_per_week,
            total_weeks=request.target_weeks,
            total_estimated_hours=round(total_hours, 1),
            status="ACTIVE",
        )
        db.add(plan)
        db.flush()

        for t in generated_tasks:
            task_obj = LearningTask(
                plan_id=plan.id,
                user_id=user.id,
                skill=t["skill"],
                title=t["title"],
                description=t["description"],
                week_number=t["week_number"],
                priority=t["priority"],
                estimated_hours=t["estimated_hours"],
                status="NOT_STARTED",
                learning_goal=t["learning_goal"],
                topics=t["topics"],
                practice_project=t["practice_project"],
                interview_question_prep=t["interview_question_prep"],
            )
            db.add(task_obj)

        db.commit()
        db.refresh(plan)

        return self._format_plan_out(plan)

    def get_active_plan(self, db: Session, user: User) -> Optional[LearningPlanOut]:
        plan = (
            db.query(LearningPlan)
            .filter(LearningPlan.user_id == user.id, LearningPlan.status == "ACTIVE")
            .order_by(LearningPlan.created_at.desc())
            .first()
        )
        if not plan:
            return None
        return self._format_plan_out(plan)

    def get_plan_by_id(self, db: Session, user: User, plan_id: str) -> LearningPlanOut:
        plan = (
            db.query(LearningPlan)
            .filter(LearningPlan.id == plan_id, LearningPlan.user_id == user.id)
            .first()
        )
        if not plan:
            raise AppException(message="Learning plan not found.", code="NOT_FOUND", status_code=404)
        return self._format_plan_out(plan)

    def get_user_plans(self, db: Session, user: User) -> List[LearningPlanOut]:
        plans = (
            db.query(LearningPlan)
            .filter(LearningPlan.user_id == user.id)
            .order_by(LearningPlan.created_at.desc())
            .all()
        )
        return [self._format_plan_out(p) for p in plans]

    def update_task_status(
        self,
        db: Session,
        user: User,
        task_id: str,
        new_status: str,
        evidence: Optional[str] = None,
    ) -> LearningTaskOut:
        task = (
            db.query(LearningTask)
            .filter(LearningTask.id == task_id, LearningTask.user_id == user.id)
            .first()
        )
        if not task:
            raise AppException(message="Learning task not found.", code="NOT_FOUND", status_code=404)

        task.status = new_status
        if evidence is not None:
            task.evidence = evidence.strip() or None

        if new_status in {"COMPLETED", "VERIFIED"}:
            task.completed_at = datetime.now(timezone.utc)
        else:
            task.completed_at = None

        db.commit()
        db.refresh(task)
        return LearningTaskOut.model_validate(task)

    def _format_plan_out(self, plan: LearningPlan) -> LearningPlanOut:
        tasks = plan.tasks or []
        completed_hours = sum(
            t.estimated_hours for t in tasks if t.status in {"COMPLETED", "VERIFIED"}
        )
        total_hours = plan.total_estimated_hours or sum(t.estimated_hours for t in tasks) or 1.0
        progress = round((completed_hours / total_hours) * 100, 1)

        sorted_tasks = sorted(tasks, key=lambda t: (t.week_number, t.created_at))

        return LearningPlanOut(
            id=plan.id,
            user_id=plan.user_id,
            job_id=plan.job_id,
            target_role=plan.target_role,
            target_company=plan.target_company,
            hours_per_week=plan.hours_per_week,
            total_weeks=plan.total_weeks,
            total_estimated_hours=plan.total_estimated_hours,
            status=plan.status,
            progress_pct=progress,
            completed_hours=round(completed_hours, 1),
            tasks=[LearningTaskOut.model_validate(t) for t in sorted_tasks],
            created_at=plan.created_at,
        )

    def _generate_tasks(
        self,
        db: Session,
        user: User,
        job: Job,
        missing_skills: List[str],
        hours_per_week: int,
        target_weeks: int,
        primary_project: str,
    ) -> List[Dict[str, Any]]:
        prompt = f"""Target Role: {job.title} at {job.company}
Candidate's Missing Skills: {', '.join(missing_skills[:8])}
Student Available Time: {hours_per_week} hours per week across {target_weeks} weeks.
Candidate Primary Project: '{primary_project}'

Generate weekly tasks fitting exactly {hours_per_week} hours/week for {target_weeks} weeks."""

        try:
            raw_response = llm_gateway.generate(
                prompt=prompt,
                system_prompt=PLAN_SYSTEM_PROMPT,
                json_mode=True,
                user_id=user.id,
                db=db,
            )
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            data = json.loads(cleaned)
            tasks = data.get("tasks", [])
            if tasks:
                return tasks
        except Exception:
            pass

        return self._generate_fallback_tasks(
            missing_skills=missing_skills,
            hours_per_week=hours_per_week,
            target_weeks=target_weeks,
            primary_project=primary_project,
        )

    def _generate_fallback_tasks(
        self,
        missing_skills: List[str],
        hours_per_week: int,
        target_weeks: int,
        primary_project: str,
    ) -> List[Dict[str, Any]]:
        tasks = []
        skills = missing_skills if missing_skills else ["Docker", "PostgreSQL", "System Design", "AWS"]
        hours_per_task = round(hours_per_week / 2, 1)

        skill_idx = 0
        for week in range(1, target_weeks + 1):
            s1 = skills[skill_idx % len(skills)]
            skill_idx += 1
            tasks.append({
                "skill": s1,
                "title": f"Master {s1} Core Fundamentals",
                "description": f"Learn key principles, best practices, and architecture of {s1}.",
                "week_number": week,
                "priority": "HIGH" if week <= 2 else "MEDIUM",
                "estimated_hours": hours_per_task,
                "learning_goal": f"Gain practical competency in {s1} required for target role.",
                "topics": [f"{s1} Basics", f"{s1} Configuration", f"Performance Tuning"],
                "practice_project": f"Integrate {s1} into '{primary_project}' to demonstrate hands-on application.",
                "interview_question_prep": f"Prepare top 10 interview questions and live debugging scenarios for {s1}.",
            })

            s2 = skills[skill_idx % len(skills)]
            skill_idx += 1
            tasks.append({
                "skill": s2,
                "title": f"Practical Application & Integration of {s2}",
                "description": f"Deep dive into real-world use cases, error handling, and deployment for {s2}.",
                "week_number": week,
                "priority": "HIGH" if week == 1 else "MEDIUM",
                "estimated_hours": hours_per_task,
                "learning_goal": f"Build tangible evidence for {s2} on your resume.",
                "topics": [f"{s2} Architecture", "API Integration", "Automated Testing"],
                "practice_project": f"Build a prototype service leveraging {s2} with proper unit tests.",
                "interview_question_prep": f"Practice whiteboarding and system trade-offs regarding {s2}.",
            })

        return tasks


learning_engine = LearningEngine()
