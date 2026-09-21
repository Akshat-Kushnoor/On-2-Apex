##--On2-Apex--##
-# On2-Apex #-
# AI PLACEMENT COACH

## Local-First Expert SWE Implementation Prompt
# ROLE

Act as a **Senior Software Engineer + AI Engineer + Software Architect** responsible for building the AI Placement Coach application locally.

You are not simply generating code snippets.

You are responsible for producing a **working, maintainable, testable application** where every completed phase integrates with the previous phases.

The goal is to build the product incrementally.

Do not attempt to build all features at once.

Complete one phase, verify it, and only then move to the next phase.

---

# PRODUCT IDEA

AI Placement Coach is a personal placement operating system for students.

The central idea is:

```text
Student Profile
      ↓
Understand Student
      ↓
Find Relevant Jobs
      ↓
Understand Job Requirements
      ↓
Compare Student vs Job
      ↓
Identify Skill Gaps
      ↓
Create Learning Plan
      ↓
Improve Profile / Resume
      ↓
Apply
      ↓
Prepare for Interview
      ↓
Measure Progress
```

The system should combine:

```text
Deterministic software
+
Database-backed student data
+
Document processing
+
LLM reasoning
+
Personalized recommendations
```

The AI must not become the source of truth.

The database and deterministic application logic should remain the source of truth.

---

# IMPORTANT DEVELOPMENT CONSTRAINT

## LOCAL DEVELOPMENT ONLY

For the current implementation:

**Do not focus on deployment.**

Do not spend implementation effort on:

* cloud deployment
* AWS
* Azure
* GCP
* Kubernetes
* production infrastructure
* cloud object storage
* production monitoring
* CI/CD
* Docker-based deployment architecture

The application should run entirely on the developer's machine.

---

# LOCAL DATABASE REQUIREMENT

Use a database stored locally inside the project.

Create/use a root-level database directory such as:

```text
db/
```

The exact internal structure is up to you.

Do not hard-code a specific repository folder structure.

The database must persist between application restarts.

Do not use an in-memory database for the actual application.

The development environment should allow:

```text
start application
        ↓
create data
        ↓
stop application
        ↓
start again
        ↓
data still exists
```

If PostgreSQL is already available locally, use it appropriately.

If the project is intended to be completely self-contained, use a local database solution such as SQLite during the local development phase.

Choose the simplest reliable option that fits the architecture.

The important requirement is:

> **Persistent local database + migrations + clean data access layer.**

---

# DO NOT FORCE A FOLDER STRUCTURE

Do NOT blindly create a prescribed repository structure.

First inspect the existing repository.

Understand:

```text
existing frontend
existing backend
existing configuration
existing dependencies
existing database
existing components
```

Then choose a structure that is:

* logical
* modular
* maintainable
* easy for another developer to understand

Explain major architectural decisions before making significant structural changes.

Do not reorganize an existing project unnecessarily.

---

# GENERAL ENGINEERING RULES

Follow these principles throughout the project.

## 1. Build incrementally

Never implement future phases prematurely.

## 2. Keep responsibilities separated

Separate:

```text
API layer
business logic
database logic
external integrations
AI logic
document processing
frontend presentation
```

Do not put everything inside API routes.

## 3. Prefer deterministic logic

If something can be reliably solved with normal code, use normal code.

Use AI where semantic reasoning is genuinely useful.

## 4. Validate everything

Validate:

```text
user input
API input
database data
uploaded files
LLM output
external API responses
```

## 5. Never trust LLM output

Every structured LLM response must be parsed and validated before being used.

## 6. Do not fabricate student information

The system must never invent:

* skills
* projects
* experience
* certifications
* achievements
* education
* technologies
* metrics

AI can rewrite or organize information.

It cannot create fake credentials.

## 7. Preserve user control

Important changes to the student's profile should be presented as proposals.

Example:

```text
Resume extracted information
        ↓
Student reviews
        ↓
Student approves
        ↓
Profile updated
```

---

# PHASE 1 — LOCAL PROJECT FOUNDATION

## Objective

Create the technical foundation required for the rest of the application.

The foundation should provide:

```text
Frontend
Backend
Local database
Database migrations
Configuration
Health checking
Logging
Error handling
Frontend ↔ Backend communication
```

Use the project's existing technology where appropriate.

The intended backend is:

```text
FastAPI
```

The intended frontend is:

```text
React
```

Use:

```text
PostgreSQL or local SQLite
```

depending on the existing local setup and architectural needs.

Use a migration system such as:

```text
Alembic
```

if using SQLAlchemy/FastAPI.

---

## Phase 1 — Step 1: Inspect the project

Before writing code:

1. Inspect the repository.
2. Identify the frontend.
3. Identify the backend.
4. Identify package managers.
5. Identify existing dependencies.
6. Identify whether a database already exists.
7. Identify existing environment configuration.
8. Identify existing API communication.
9. Identify reusable code.

Do not overwrite working code unnecessarily.

---

## Phase 1 — Step 2: Establish configuration

Create a clean configuration system.

Configuration should support:

```text
database location
API configuration
frontend/backend URLs
LLM configuration placeholders
development settings
```

Secrets must not be committed.

Provide an example environment configuration file if needed.

Never hard-code API keys.

---

## Phase 1 — Step 3: Establish database access

Create a proper database abstraction.

Requirements:

```text
database connection
session management
models
migrations
initial migration
```

The database must persist locally.

Do not create business logic directly inside database connection code.

---

## Phase 1 — Step 4: Health endpoints

Create:

```text
GET /health
GET /ready
```

`/health` should answer whether the backend process is alive.

`/ready` should verify that required local dependencies are usable.

For example:

```text
Backend running
+
Database accessible
```

Do not make `/health` perform expensive operations.

---

## Phase 1 — Step 5: Logging

Introduce useful development logging.

Log things such as:

```text
request received
request completed
database errors
external service failures
background task failures
```

Never log:

```text
passwords
API keys
authentication tokens
sensitive user data unnecessarily
```

---

## Phase 1 — Step 6: Error handling

Create consistent API errors.

For example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request"
  }
}
```

Do not expose internal stack traces to the frontend.

Keep detailed errors available to the developer through logs.

---

## Phase 1 — Step 7: Frontend/backend connection

Create a minimal frontend test page that verifies communication with the backend.

For example:

```text
AI Placement Coach

Backend:
Connected ✓

Database:
Ready ✓
```

This is only a foundation test.

Do not spend time polishing the UI yet.

---

## Phase 1 acceptance criteria

Phase 1 is complete only when:

```text
[ ] Frontend starts locally
[ ] Backend starts locally
[ ] Local database is persistent
[ ] Database migrations work
[ ] /health works
[ ] /ready works
[ ] Frontend communicates with backend
[ ] Configuration works
[ ] Errors are handled
[ ] Secrets are not committed
```

Before proceeding, actually test the complete startup flow.

---

# PHASE 2 — AUTHENTICATION + STUDENT PROFILE

## Objective

Create the student's persistent identity and professional profile.

The profile becomes the foundation for almost every future feature.

The system should eventually understand:

```text
Who is the student?
What are their skills?
What have they built?
What are they studying?
What roles do they want?
Where do they want to work?
What experience do they have?
```

---

# Phase 2 — Step 1: Authentication

Implement basic local authentication.

At minimum:

```text
registration
login
logout
authenticated requests
```

Passwords must never be stored as plaintext.

Use secure password hashing.

The backend must verify authentication for protected profile endpoints.

---

# Phase 2 — Step 2: Student profile

Create a profile that can represent:

```text
Name
Email
Phone
Location
College
Degree
Branch
Graduation year
CGPA
Preferred roles
Preferred locations
Work authorization
```

The model should be extensible.

Do not put every possible future field into one enormous table if separate entities make more sense.

---

# Phase 2 — Step 3: Skills

A student can have multiple skills.

Examples:

```text
Python
C++
JavaScript
React
Node.js
MongoDB
PostgreSQL
Docker
Git
Machine Learning
```

The system should eventually be able to distinguish:

```text
skill name
skill category
proficiency
evidence
```

Do not over-engineer proficiency initially.

Start with the minimum useful representation.

---

# Phase 2 — Step 4: Education

Support multiple education records where appropriate.

For example:

```text
Degree
Institution
Branch
Start year
End year
CGPA
```

The system should not assume a student has only one educational record.

---

# Phase 2 — Step 5: Projects

Projects are extremely important because they will later be used for:

```text
job matching
resume generation
interview preparation
skill evidence
```

Each project should be able to represent:

```text
title
description
technologies
role
links
achievements
```

Do not force students to describe projects using only AI-generated text.

The student's actual project information remains authoritative.

---

# Phase 2 — Step 6: Experience

Support:

```text
company
role
start date
end date
description
technologies
achievements
```

---

# Phase 2 — Step 7: Certifications and achievements

Support structured records for:

```text
certifications
achievements
awards
hackathons
competitive programming
other relevant accomplishments
```

Keep these extensible.

---

# Phase 2 — Step 8: API

Create the required APIs:

```text
GET /profile
PUT /profile

GET /profile/skills
POST /profile/skills
DELETE /profile/skills/{id}

GET /profile/projects
POST /profile/projects
PUT /profile/projects/{id}
DELETE /profile/projects/{id}
```

Add equivalent endpoints for other profile sections where required.

Every endpoint must:

```text
authenticate user
validate input
verify ownership
return structured response
handle errors
```

A user must never be able to access another user's profile data.

---

# Phase 2 — Step 9: Frontend

Create functional screens for:

```text
Onboarding
Profile
Skills
Education
Projects
Experience
```

Focus on usability rather than visual perfection.

The student should be able to:

```text
create profile
edit profile
add skill
remove skill
add project
edit project
delete project
add education
add experience
```

Changes must persist after refreshing the page.

---

# Phase 2 acceptance criteria

```text
[ ] User can register
[ ] User can log in
[ ] Protected APIs require authentication
[ ] Student profile persists
[ ] Skills persist
[ ] Projects persist
[ ] Education persists
[ ] Experience persists
[ ] User ownership is enforced
[ ] Frontend forms validate input
[ ] Backend validates input
[ ] Data survives application restart
```

---

# PHASE 3 — JOB INTELLIGENCE

## Objective

Build the job discovery system.

The system should convert messy external job data into a consistent internal representation.

The student should eventually be able to say:

```text
I want software engineering jobs
in Bengaluru
with Python and React
for fresher/entry-level roles.
```

and receive normalized jobs.

---

# Phase 3 — Step 1: Job search input

Support:

```json
{
  "role": "",
  "location": "",
  "keywords": [],
  "experience": ""
}
```

Validate search parameters.

---

# Phase 3 — Step 2: Job ingestion

Use JobSpy or an appropriate job-search integration.

Do not tightly couple the entire application to JobSpy.

Create an abstraction similar to:

```text
Job Source
    ↓
Raw Job
    ↓
Normalizer
    ↓
Internal Job
```

This allows additional sources later.

---

# Phase 3 — Step 3: Normalize jobs

Every job should become approximately:

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

The internal model may contain additional metadata where useful.

---

# Phase 3 — Step 4: Normalization

Normalize:

```text
company
title
URL
location
```

For example:

```text
"Google LLC"
"google"
"GOOGLE"
```

should be handled consistently when deduplicating.

URLs should be canonicalized where practical.

---

# Phase 3 — Step 5: Deduplication

Use a deterministic deduplication strategy based on:

```text
normalized company
+
normalized title
+
canonical URL
```

Be careful with jobs that have:

```text
same title
same company
different locations
```

Do not accidentally merge genuinely different jobs.

---

# Phase 3 — Step 6: Failure handling

Job retrieval is an external dependency.

It can fail.

Handle:

```text
timeouts
rate limits
invalid results
duplicate results
source failures
partial results
network failures
```

A failed source should not crash the entire backend.

If some sources succeed and others fail, return the successful results and expose useful status information.

---

# Phase 3 — Step 7: Background processing

Large searches should not block the API request indefinitely.

Introduce background processing where appropriate.

The user should eventually be able to see:

```text
Searching...
Found 12 jobs
Source A completed
Source B failed
```

rather than experiencing a frozen interface.

---

# Phase 3 acceptance criteria

```text
[ ] Search accepts role/location/keywords/experience
[ ] Jobs can be retrieved
[ ] Jobs are normalized
[ ] Duplicate jobs are handled
[ ] External failures are handled
[ ] Invalid jobs do not corrupt the database
[ ] Jobs persist locally
[ ] Job source is recorded
```

---

# PHAE 3.1 — JOB SEARCH API + UI

## Backend

Create:

```text
POST /jobs/search
GET /jobs
GET /jobs/{job_id}
POST /jobs/{job_id}/save
DELETE /jobs/{job_id}/save
```

Add filtering/pagination where appropriate.

Do not load thousands of jobs into the frontend unnecessarily.

---

# Frontend

Create:

```text
Job Search
Job Feed
Job Details
Saved Jobs
```

A job card should show:

```text
Role
Company
Location
Source
Posted date
Experience
Skills
```

At this stage:

**Do not show an AI-generated match score.**

The skill-gap engine has not been implemented yet.

You may show:

```text
Match analysis not available yet
```

or simply omit it.

---

# PHASE 4 — DOCUMENT INTELLIGENCE

## Objective

Allow the student to upload a resume and convert it into structured information.

The system should understand the resume without immediately modifying the student's profile.

The core philosophy is:

```text
Resume
 ↓
Extract
 ↓
Understand
 ↓
Propose
 ↓
Student reviews
 ↓
Student approves
 ↓
Profile updates
```

---

# Phase 4 — Step 1: Resume upload

Support PDF resume uploads.

Validate:

```text
file type
file size
filename
content
```

Never trust the uploaded filename.

Generate a safe internal filename or identifier.

Store the original file locally.

---

# Phase 4 — Step 2: Document processing

Use Docling.

Pipeline:

```text
PDF
 ↓
Validation
 ↓
Local storage
 ↓
Docling
 ↓
Markdown
```

Preserve the generated Markdown.

The Markdown becomes an intermediate representation useful for:

```text
inspection
debugging
LLM processing
future reprocessing
```

---

# Phase 4 — Step 3: Structured extraction

Extract:

```text
skills
education
projects
experience
certifications
achievements
```

Use an appropriate combination of:

```text
document structure
deterministic parsing
LLM reasoning
```

Do not use an LLM for everything.

For example, obvious headings and text structure may be processed deterministically.

---

# PHASE 4 — STRUCTURED RESUME SCHEMA

Create a structured representation:

```json
{
  "skills": [],
  "education": [],
  "projects": [],
  "experience": [],
  "certifications": [],
  "achievements": []
}
```

Each extracted item should preserve provenance where practical.

For example:

```json
{
  "value": "React",
  "source": "resume.pdf",
  "confidence": 0.94
}
```

The exact schema can be improved as implementation progresses.

---

# IMPORTANT — EXTRACTION IS NOT TRUTH

The extraction system may make mistakes.

Therefore:

```text
Extracted Resume Data
        ↓
Validation
        ↓
Student Review
        ↓
Approve / Reject / Edit
        ↓
Profile Update
```

Never automatically overwrite existing student data.

If the resume says:

```text
React
```

the system may propose:

```text
Add React to skills
```

The student decides whether to accept it.

---

# PHASE 4 acceptance criteria

```text
[ ] PDF can be uploaded
[ ] Invalid files are rejected
[ ] Original PDF is stored locally
[ ] Docling successfully processes valid resumes
[ ] Markdown is generated
[ ] Structured extraction works
[ ] Extraction is validated
[ ] Provenance is preserved where practical
[ ] Student can review extracted information
[ ] Student can approve/reject/edit proposed changes
[ ] Profile is not automatically overwritten
```

---

# PHASE 5 — JOB DESCRIPTION INTELLIGENCE

## Objective

Convert an unstructured job description into structured requirements.

This is the first major AI intelligence layer.

The system should transform:

```text
Raw Job Description
        ↓
Preprocessing
        ↓
LLM
        ↓
Structured Requirements
```

---

# PHASE 5 — Step 1: Preprocess JD

Before sending a JD to the LLM:

```text
remove unnecessary noise
normalize whitespace
remove duplicated sections
preserve important content
```

Do not aggressively remove information that could affect job requirements.

---

# PHASE 5 — Step 2: Structured requirements

Extract:

```json
{
  "role": "",
  "required_skills": [],
  "preferred_skills": [],
  "education_requirements": [],
  "experience_requirements": [],
  "responsibilities": [],
  "tools": [],
  "interview_topics": []
}
```

You may extend this schema if implementation reveals a genuine requirement.

---

# PHASE 5 — Step 3: LLM output validation

The LLM must produce structured output.

The backend must:

```text
receive response
 ↓
parse JSON
 ↓
validate schema
 ↓
validate business rules
 ↓
store
```

Never directly trust raw LLM output.

If the output is invalid:

```text
retry
 ↓
repair
 ↓
validate
```

If it still fails:

```text
controlled failure
```

---

# PHASE 5 — Step 4: Cache job analysis

A job description may be analyzed multiple times.

Do not repeatedly spend LLM calls on identical content.

Create a deterministic hash based on the relevant job description content.

Use something conceptually like:

```text
JD hash
+
parser version
+
model/prompt version
```

as the analysis identity.

If the same job has already been analyzed with the same analysis version, reuse the stored result.

---

# PHASE 5 acceptance criteria

```text
[ ] JD can be analyzed
[ ] Requirements are structured
[ ] LLM output is validated
[ ] Invalid outputs are handled
[ ] Analysis is stored
[ ] Duplicate analysis is avoided
[ ] Prompt/model version can be tracked
```

---

# PHASE 6 — SKILL GAP ENGINE

## Objective

Answer the central question:

> "Given this student and this job, what is the student's current alignment and what should they do next?"

Inputs:

```text
Student Profile
+
Approved Resume Information
+
Job Requirements
```

Output:

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

---

# CRITICAL DESIGN RULE

The LLM must NOT be responsible for the final numerical match score.

The score should come from deterministic application logic.

The LLM can help with:

```text
semantic matching
explanations
recommendations
contextual interpretation
```

But the final score must be reproducible.

---

# PHASE 6 — STEP 1: Deterministic scoring

Build a scoring engine.

Potential inputs:

```text
required skill coverage
preferred skill coverage
experience alignment
education alignment
project relevance
```

Do not blindly use arbitrary weights.

Make weights configurable.

For example:

```text
required skills → high importance
preferred skills → lower importance
experience → configurable
education → configurable
project evidence → configurable
```

The exact weighting should live in configuration/business logic rather than being buried inside an LLM prompt.

---

# PHASE 6 — STEP 2: Skill normalization

Students and jobs may describe the same concept differently.

For example:

```text
JavaScript
JS
ECMAScript
```

or:

```text
Postgres
PostgreSQL
```

Create a skill normalization mechanism.

Start simple.

Do not attempt to build a universal ontology immediately.

The system should be extensible later.

---

# PHASE 6 — STEP 3: Semantic matching

Use the LLM only where deterministic string matching is insufficient.

For example:

```text
Student:
"Built REST APIs using Express."

Job:
"Experience developing backend APIs with Node.js."
```

The system may identify a semantic relationship.

But this relationship should be represented explicitly and explainably.

---

# PHASE 6 — STEP 4: Explain the result

Return:

```text
Matched skills
Missing skills
Evidence
Reasons
Recommended actions
```

The explanation should reference actual student data.

Never say:

```text
You are strong in Kubernetes.
```

if the student's profile contains no evidence for Kubernetes.

---

# PHASE 6 — STEP 5: Action plan

Generate actions from the identified gaps.

For example:

```text
Missing:
Docker

Action:
1. Learn Docker fundamentals.
2. Containerize an existing project.
3. Deploy/run it locally.
4. Add Docker experience to the project documentation.
5. Practice Docker interview questions.
```

Do not automatically claim that the student has acquired the skill after completing a task.

The system should distinguish:

```text
recommended
in progress
completed
evidence added
```

---

# PHASE 6 acceptance criteria

```text
[ ] Student/job comparison works
[ ] Match score is deterministic
[ ] Required/preferred skills are distinguished
[ ] Skill normalization works
[ ] Semantic matching can be used where required
[ ] Missing skills are identified
[ ] Explanations reference actual evidence
[ ] Action plan is generated
[ ] Results are persisted
```

---

# PHASE 6 — MATCH EXPLANATION UI

The job details page should now evolve.

Show:

```text
YOUR MATCH

Overall alignment: XX%

Why you match

✓ Python
✓ React
✓ REST APIs

Potential gaps

△ Docker
△ AWS
△ System Design
```

Then:

```text
WHY THESE GAPS MATTER
```

Then:

```text
WHAT TO DO NEXT
```

The UI should clearly distinguish:

```text
Existing evidence
vs
AI inference
vs
Recommended action
```

Do not present AI inference as verified fact.

---

# PHASE 7 — PERSONALIZED LEARNING ENGINE

## Objective

Turn skill gaps into a realistic learning plan.

The learning engine should answer:

> "Given what this student already knows, what they are missing for this target job, and how much time they have, what should they work on next?"

---

# INPUTS

Use:

```text
Current skills
Target job
Missing skills
Time available
Interview date
```

If interview date is unavailable, do not invent one.

---

# PHASE 7 — STEP 1: Prioritize gaps

Not every missing skill deserves equal attention.

Prioritize using information such as:

```text
required vs preferred
importance to target role
current skill distance
estimated learning effort
interview relevance
```

The prioritization should be explainable.

---

# PHASE 7 — STEP 2: Generate learning plan

Convert gaps into:

```text
Learning Goal
    ↓
Topics
    ↓
Practice
    ↓
Project/application
    ↓
Assessment
```

For example:

```text
Goal:
Learn Docker sufficiently for backend interviews.

Topics:
- images
- containers
- Dockerfiles
- volumes
- networking

Practice:
Containerize an existing Node.js project.

Assessment:
Explain Docker architecture and troubleshoot a container.
```

---

# PHASE 7 — STEP 3: Respect available time

The user may specify:

```text
10 hours/week
```

The system must produce a plan that fits approximately within that constraint.

Do not generate:

```text
40 hours of tasks
```

for a student who has only:

```text
10 hours available
```

The system should estimate:

```text
task duration
total duration
weekly workload
```

---

# PHASE 7 — STEP 4: Learning task model

Represent individual tasks in the database.

A task should be able to contain:

```text
skill
title
description
priority
estimated time
status
deadline
evidence
```

Statuses can include:

```text
Not Started
In Progress
Completed
Verified
```

Initially, completion can be student-reported.

Later versions can introduce evidence-based verification.

---

# PHASE 7 — STEP 5: Connect learning to the target job

The learning plan should not become a generic Udemy-style course.

Every recommendation should answer:

```text
Why am I learning this?

Which job requirement does it address?

How will I demonstrate it?

How does it affect my interview preparation?
```

For example:

```text
Job requirement:
Docker

Learning task:
Containerize your MERN application.

Evidence:
GitHub repository + project documentation.

Interview preparation:
Explain Dockerfile, image, container, networking.
```

This creates the core loop:

```text
Job Requirement
      ↓
Skill Gap
      ↓
Learning
      ↓
Project Evidence
      ↓
Resume Evidence
      ↓
Interview Preparation
```

---

# PHASE 7 acceptance criteria

```text
[ ] Learning plan can be generated from skill gaps
[ ] Missing skills are prioritized
[ ] Time availability is respected
[ ] Tasks have estimated effort
[ ] Tasks persist locally
[ ] Tasks have statuses
[ ] Learning is connected to job requirements
[ ] Student can update progress
[ ] Plan can be regenerated when circumstances change
```

---

# END-TO-END CHECKPOINT

After Phase 7, the application should support the following complete local workflow:

```text
REGISTER
   ↓
CREATE STUDENT PROFILE
   ↓
ADD SKILLS / PROJECTS / EDUCATION
   ↓
UPLOAD RESUME
   ↓
EXTRACT RESUME INFORMATION
   ↓
REVIEW EXTRACTION
   ↓
APPROVE PROFILE INFORMATION
   ↓
SEARCH JOBS
   ↓
SAVE JOB
   ↓
OPEN JOB
   ↓
ANALYZE JOB DESCRIPTION
   ↓
COMPARE STUDENT WITH JOB
   ↓
VIEW MATCH EXPLANATION
   ↓
VIEW SKILL GAPS
   ↓
GENERATE LEARNING PLAN
   ↓
TRACK LEARNING TASKS
```

All of this must work using the local environment.

---

# HOW YOU MUST WORK

For every phase:

## STEP 1 — Inspect

Understand what currently exists.

Do not assume the repository is empty.

---

## STEP 2 — Explain

Before significant implementation, briefly explain:

```text
What we are building
Why it is needed
How it connects to previous phases
Important architectural decisions
```

---

## STEP 3 — Implement

Implement only the current phase.

Do not silently implement future functionality.

---

## STEP 4 — Test

Test the actual feature.

Do not merely state that it should work.

Where possible, run:

```text
backend tests
frontend tests
API tests
database tests
integration tests
```

---

## STEP 5 — Review

Check:

```text
correctness
security
data ownership
error handling
LLM reliability
database persistence
frontend/backend consistency
```

---

## STEP 6 — Report

At the end of each phase, provide:

```text
PHASE COMPLETED

Implemented:
...

Important decisions:
...

Database changes:
...

API changes:
...

Frontend changes:
...

Tests performed:
...

Known limitations:
...

Next recommended phase:
...
```

Then stop.

Do not automatically continue to the next phase.

---

# MOST IMPORTANT PRODUCT PRINCIPLE

The product is NOT:

```text
Resume Generator + Chatbot
```

The product is:

# A continuously updated placement intelligence system.

Its central loop is:

```text
Student
   ↓
Target Role
   ↓
Job
   ↓
Requirements
   ↓
Skill Gap
   ↓
Learning Plan
   ↓
Evidence
   ↓
Resume
   ↓
Application
   ↓
Interview
   ↓
Feedback
   ↓
Improved Student Profile
```

Every future feature should strengthen this loop.

---

# ENGINEERING PRINCIPLE

Use:

```text
Database
    ↓
Source of truth

Deterministic logic
    ↓
Calculations / validation / business rules

LLM
    ↓
Reasoning / semantic interpretation / recommendations

User
    ↓
Approval / correction / important decisions
```

Do not allow:

```text
LLM
 ↓
Direct database mutation
```

without validation and appropriate application-level control.

---

# START NOW

Begin with:

# PHASE 1 — PROJECT FOUNDATION

First inspect the existing repository.

Do not assume a folder structure.

Do not implement future phases.

Do not focus on deployment.

Build a clean local foundation that the subsequent profile, job, document, AI, matching, and learning systems can safely build upon.
