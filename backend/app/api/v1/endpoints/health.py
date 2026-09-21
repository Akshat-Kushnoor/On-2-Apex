from pathlib import Path
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.errors import AppException
from app.core.logging import logger
from app.db.session import get_db

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness probe: verifies the backend API process is up."""
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: verifies local database and storage dependencies."""
    checks = {}

    # 1. Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as exc:
        logger.error(f"Readiness check failed on database: {exc}")
        raise AppException(
            message="Database is not reachable.",
            code="DATABASE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"error": str(exc)},
        )

    # 2. Local storage / db directory check
    try:
        if settings.DATABASE_URL.startswith("sqlite:///"):
            db_file_str = settings.DATABASE_URL.replace("sqlite:///", "")
            db_dir = Path(db_file_str).resolve().parent
            if not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
            checks["local_db_directory"] = "accessible"
        else:
            checks["database_type"] = "remote"
    except Exception as exc:
        logger.error(f"Readiness check failed on filesystem: {exc}")
        raise AppException(
            message="Local storage path is not writable.",
            code="STORAGE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"error": str(exc)},
        )

    return {
        "status": "ready",
        "checks": checks,
    }
