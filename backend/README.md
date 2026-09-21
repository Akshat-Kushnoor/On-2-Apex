# AI Placement Coach - Backend API

Production-grade FastAPI backend managed with Astral's `uv`.

## Features (Phase 1 Foundation)
- **FastAPI** with async lifespan and standardized CORS configuration for Next.js.
- **Pydantic v2 & Pydantic-Settings** for centralized configuration and `.env` parsing.
- **SQLite Database** with WAL mode enabled, located persistently at `../db/placement_coach.db`.
- **Automatic Schema Initialization** on server startup (`Base.metadata.create_all(bind=engine)`), eliminating the need for manual migration commands during local development.
- **Unified Error Handling** ensuring standard error JSON envelopes:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message"
    }
  }
  ```
- **Logging Middleware** providing timing and non-sensitive logging.
- **Health & Readiness Endpoints**:
  - `GET /health` / `GET /api/v1/health` (process liveness)
  - `GET /ready` / `GET /api/v1/ready` (database and storage health check)

---

## Getting Started

### 1. Requirements
- Python 3.13+ or 3.14
- [uv](https://github.com/astral-sh/uv) installed

### 2. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```

### 3. Run Development Server
The database and tables are created automatically on boot:
```bash
uv run uvicorn main:app --reload --port 8000
```
- API Docs: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Readiness Check: [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)

### 4. Run Automated Tests
```bash
uv run pytest
```
