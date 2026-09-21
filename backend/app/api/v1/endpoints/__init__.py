from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.job_analysis import router as job_analysis_router
from app.api.v1.endpoints.job_match import router as job_match_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.learning import router as learning_router
from app.api.v1.endpoints.llm import router as llm_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.resumes import router as resumes_router
from app.api.v1.endpoints.workspace import router as workspace_router
from app.api.v1.endpoints.google import router as google_router

__all__ = [
    "auth_router",
    "documents_router",
    "health_router",
    "job_analysis_router",
    "job_match_router",
    "jobs_router",
    "learning_router",
    "llm_router",
    "profile_router",
    "resumes_router",
    "workspace_router",
    "google_router",
]
