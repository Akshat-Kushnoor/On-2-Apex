# AI Placement Coach — Detailed Team Build Guide

## 1. System Architecture

```text
React + Tailwind
      ↓
FastAPI Backend
      ↓
├── JobSpy Service
├── Document Service
├── Placement Engine
├── LLM Gateway
├── Google Service
└── User Workspace
      ↓
PostgreSQL + File Storage
```

## 2. Repository Structure

```text
/backend
  /api
  /services
    job_scraper.py
    document_engine.py
    placement_engine.py
    resume_generator.py
    llm_gateway.py
    google_service.py
  /models
  /schemas
  main.py

/frontend
  /pages
  /components
  /services
```

## 3. Job Scraping

Install:

```bash
pip install -U python-jobspy
```

Create `job_scraper.py`.

Inputs: `role`, `location`, `keywords`, `experience`.

Normalize every job into:

```json
{
  "title": "",
  "company": "",
  "location": "",
  "description": "",
  "url": "",
  "source": "",
  "posted_at": ""
}
```

Deduplicate using normalized `company + title + url`.

Respect source terms, rate limits and applicable site policies.

## 4. Resume/PDF Processing

Install Docling and create `document_engine.py`.

```text
Resume.pdf
   ↓
Docling
   ↓
resume.md
   ↓
Structured Student JSON
```

Store both original PDF and Markdown inside the user's workspace.

Student JSON should contain:

`skills, education, projects, experience, certifications, achievements`.

## 5. Job Intelligence

For every selected job:

```text
Job Description
      ↓
LLM
      ↓
job.md + structured requirements
```

Compare:

```text
Student Profile
       +
resume.md
       +
job requirements
```

Return strict JSON:

```json
{
  "match_score": 0,
  "matched_skills": [],
  "missing_skills": [],
  "resume_highlights": [],
  "learning_priorities": [],
  "interview_topics": [],
  "action_plan": []
}
```

Validate every LLM response against a Pydantic schema.

## 6. Resume Generation

```text
Student JSON + Job Requirements
          ↓
        LLM
          ↓
      resume.tex
          ↓
   isolated subprocess
          ↓
      resume.pdf
```

Never execute arbitrary generated commands. Restrict compilation to an isolated temporary directory and timeout the process.

## 7. LLM BYOK Gateway

Create one interface:

```python
generate(prompt, provider, model, api_key)
```

Implement adapters for:

* OpenRouter
* Gemini
* Groq
* NVIDIA NIM

The application communicates only with the gateway, never directly with providers.

## 8. Google Integration

Use OAuth 2.0.

**Calendar:** create interview/preparation events.

**Gmail:** send application/reminder notifications.

Store OAuth tokens securely and request only required scopes.

## 9. Build Sequence

```text
P0 → Auth + DB + Student Profile
P0 → JobSpy + Job Storage
P0 → Docling + JD Parser
P0 → Skill Gap Engine

P1 → Resume Generator
P1 → Master Features
P1 → BYOK Gateway

P2 → Calendar + Gmail
P2 → Adaptive Mock Interview
P2 → Readiness Score

P3 → Placement Twin
P3 → Recruiter Simulation
```

## 10. Team Ownership

**Frontend:** Dashboard, profile, job comparison, roadmap.

**Backend:** APIs, database, authentication.

**Scraping:** JobSpy + normalization + deduplication.

**AI:** LLM gateway + skill-gap + recommendations.

**Documents:** Docling + Markdown + LaTeX/PDF.

**Integrations:** Google OAuth + Calendar + Gmail.

**All:** API contracts, testing, security and final demo integration.
