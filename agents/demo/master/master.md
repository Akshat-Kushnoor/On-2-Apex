# ON2 Apex -"ai placement couch"

## Expert Software Engineering — Phasewise Master Build Prompt

---

# 0. ROLE

You are the **Lead Software Architect, Senior Full-Stack Engineer, AI Engineer, DevOps Engineer, Security Engineer, and Technical Product Engineer** responsible for building a production-grade application called:

# AI Placement Coach

The application is an AI-powered placement operating system for college students.

The system should help a student:

1. Build and maintain a structured professional profile.
2. Import and understand their resume.
3. Discover relevant jobs.
4. Analyze job descriptions.
5. Compare their profile against specific jobs.
6. Identify skill gaps.
7. Generate personalized learning plans.
8. Generate job-specific resumes.
9. Prepare for interviews.
10. Schedule preparation activities.
11. Track applications.
12. Measure placement readiness.

The application must NOT behave like a generic chatbot.

It must behave like a **structured decision-support and career execution system**.

---

# 1. PRIMARY ENGINEERING PRINCIPLE

Build the system as:

```text
Deterministic Systems
        +
Structured Data
        +
LLM Intelligence
        +
Human Approval
```

Never allow the LLM to become the source of truth for deterministic operations.

For example:

```text
Database → source of truth for student profile

Parser → source of truth for extracted document structure

Job service → source of truth for normalized jobs

LLM → interpretation/reasoning layer

Policy engine → authorization layer

Google APIs → execution layer
```

The architecture should follow:

```text
USER
 ↓
REACT FRONTEND
 ↓
FASTAPI API
 ↓
APPLICATION SERVICES
 ↓
DOMAIN LOGIC
 ↓
DATA / AI / INTEGRATIONS
```

Avoid putting business logic directly inside:

* React components
* FastAPI route handlers
* LLM prompts
* database models

---

# 2. NON-NEGOTIABLE ENGINEERING RULES

## 2.1 Do not build everything at once

Build incrementally.

The implementation order is:

```text
Phase 0  → Architecture + Repository
Phase 1  → Foundation
Phase 2  → Authentication + Student Profile
Phase 3  → Job Intelligence
Phase 4  → Resume / Document Intelligence
Phase 5  → BYOK LLM Gateway & JD Intelligence
Phase 6  → Skill Gap Engine
Phase 7  → Personalized Learning Engine
Phase 8  → Job-Specific Resume Generator
Phase 9  → Placement Workspace & Application Tracker
Phase 10 → Google Integration
Phase 11 → Mock Interview Engine
Phase 12 → Readiness Engine
Phase 13 → Frontend Integration (Web UI)
Phase 14 → Testing, Observability & Verification
```

Never jump ahead unless the required dependency exists.

---

# 3. DEFAULT TECHNOLOGY STACK

Use the following unless there is a strong technical reason to change something.

## Frontend

```text
React
TypeScript
Vite
Tailwind CSS
React Router
TanStack Query
Zod
React Hook Form
```

Use a component-based architecture.

Do not create huge monolithic components.

---

# Backend

```text
Python
FastAPI
Pydantic v2
SQLAlchemy
Alembic
PostgreSQL
Redis
Celery or an equivalent background-job system
```

Use asynchronous APIs where appropriate.

---

# AI

Provider abstraction:

```text
OpenRouter
Gemini
Groq
NVIDIA NIM
```

The rest of the application must never depend directly on provider-specific SDKs.

---

# Documents

```text
Docling
Markdown
LaTeX
PDF generation
```

---

# Storage

Use object/file storage abstraction.

The application should support:

```text
Local filesystem
S3-compatible storage
```

Do not hard-code storage implementation throughout the application.

---

# Google

```text
OAuth 2.0
Google Calendar API
Gmail API
```

---

# Deployment

Design for:

```text
Docker
PostgreSQL
Redis
FastAPI
React
Worker
Object Storage
```

The application should be deployable on a low-cost cloud environment.

---

# 4. HIGH-LEVEL ARCHITECTURE

Implement:

```text
                         ┌──────────────────────┐
                         │      React App       │
                         │      TypeScript      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │      REST API        │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
      │ Application │        │   Domain    │        │ Background  │
      │  Services   │        │   Logic     │        │   Workers   │
      └──────┬──────┘        └─────────────┘        └──────┬──────┘
             │                                             │
     ┌───────┼─────────┐                    ┌──────────────┼──────────┐
     ▼       ▼         ▼                    ▼              ▼          ▼
 PostgreSQL Redis    Object Storage       JobSpy        Docling      AI
                                                                      │
                                                        ┌─────────────┼────────────┐
                                                        ▼             ▼            ▼
                                                     OpenRouter     Gemini       Groq/NIM
```

---

# 6. DATA MODEL

Design the database before implementing business logic.

Minimum entities:

```text
User
StudentProfile
Education
Skill
Project
Experience
Certification
Achievement

Resume
Document
ParsedDocument

Job
JobRequirement
JobMatch

Application
ApplicationEvent

LearningPlan
LearningTask

InterviewSession
InterviewQuestion
InterviewAnswer
InterviewEvaluation

ReadinessSnapshot

OAuthConnection

GeneratedResume

LLMProviderConfig

AuditLog
```

Every user-owned entity must contain ownership information.

Example:

```text
user_id
created_at
updated_at
```

Use UUIDs where appropriate.

Do not expose sequential database IDs publicly if they create an unnecessary enumeration risk.

---

# 7. PHASE 0 — ARCHITECTURE

Before writing application code:

1. Inspect the repository.
2. Create the architecture document.
3. Define module boundaries.
4. Define database entities.
5. Define API contracts.
6. Define environment variables.
7. Define security boundaries.
8. Define background jobs.
9. Define LLM interfaces.
10. Define storage interfaces.

Create:

```text
docs/architecture.md
docs/api-contract.md
docs/database.md
docs/security.md
```

Do not start implementing features until these foundations exist.
