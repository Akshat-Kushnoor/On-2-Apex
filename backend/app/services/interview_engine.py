import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.models.interview import InterviewSession
from app.models.user import User
from app.schemas.interview import (
    InterviewAnswerItem,
    InterviewEvaluateRequest,
    InterviewQuestionItem,
    InterviewScorecardOut,
    InterviewStartResponse,
)
from app.services.llm_gateway import llm_gateway


ROLE_QUESTION_PRESETS: Dict[str, List[Dict[str, str]]] = {
    "backend": [
        {
            "id": 1,
            "category": "technical",
            "title": "Database Concurrency & Indexing",
            "question": "How do you prevent race conditions and handle high write concurrency in relational databases? Explain indexing trade-offs and transaction isolation levels.",
            "hint": "Mention ACID, pessimistic vs optimistic locking, B-tree indexes, and read replicas.",
        },
        {
            "id": 2,
            "category": "problem_solving",
            "title": "System Bottleneck & Caching",
            "question": "A critical API endpoint response time spiked from 50ms to 2500ms under 5x traffic. Walk me through your step-by-step diagnostic and remediation strategy.",
            "hint": "Discuss APM profiling, slow query logs, Redis caching strategies, connection pooling, and horizontal scaling.",
        },
        {
            "id": 3,
            "category": "behavioural",
            "title": "Production Incident & Communication",
            "question": "Tell me about a time you introduced a bug that broke production or faced a high-severity outage. How did you communicate with stakeholders and resolve it?",
            "hint": "Use the STAR method: Situation, Task, Action taken, and post-mortem / long-term Result.",
        },
    ],
    "frontend": [
        {
            "id": 1,
            "category": "technical",
            "title": "Rendering Performance & Core Web Vitals",
            "question": "Explain how you optimize Core Web Vitals (LCP, INP, CLS) in a large Next.js/React application. How do React Server Components influence bundle sizes?",
            "hint": "Cover code splitting, dynamic imports, image optimization, memoization, and streaming SSR.",
        },
        {
            "id": 2,
            "category": "problem_solving",
            "title": "State Architecture & Race Conditions",
            "question": "Imagine a complex data dashboard where rapid user filter toggles cause outdated asynchronous search requests to overwrite fresh data. How do you eliminate this race condition?",
            "hint": "Mention AbortController, request debouncing, TanStack Query key invalidation, or redux-saga cancellation.",
        },
        {
            "id": 3,
            "category": "behavioural",
            "title": "Design Disagreement & Compromise",
            "question": "Describe a scenario where product management or design requested a feature that was technically impractical or had severe performance implications. How did you align?",
            "hint": "Highlight empathy, data-driven alternatives, phased rollouts, and collaborative consensus.",
        },
    ],
    "ai_ml": [
        {
            "id": 1,
            "category": "technical",
            "title": "Model Serving & Quantization",
            "question": "Explain the architectural trade-offs between full-precision model inference versus quantized models (INT8/FP4). How do KV-caching and batching impact GPU throughput?",
            "hint": "Discuss vLLM/TGI, memory bandwidth limits, latency vs throughput, and speculative decoding.",
        },
        {
            "id": 2,
            "category": "problem_solving",
            "title": "Hallucination & Retrieval Drift",
            "question": "Your production RAG system is retrieving irrelevant context chunks and generating subtle hallucinations on domain-specific queries. How do you diagnose and fix the retrieval pipeline?",
            "hint": "Address semantic chunking, re-ranking, hybrid vector-BM25 search, embedding fine-tuning, and guardrails.",
        },
        {
            "id": 3,
            "category": "behavioural",
            "title": "Managing Ambiguity & Research Pivots",
            "question": "Tell me about a machine learning project where experimental results failed to meet accuracy thresholds after weeks of research. How did you pivot and communicate the outcome?",
            "hint": "Structure with STAR: focus on disciplined fail-fast benchmarks, stakeholder alignment, and reusable learnings.",
        },
    ],
    "fullstack": [
        {
            "id": 1,
            "category": "technical",
            "title": "End-to-End Type Safety & Data Flow",
            "question": "How do you architect end-to-end type safety and resilient state synchronization across the frontend, REST/GraphQL APIs, and database layers in a modern microservice or modular monolith?",
            "hint": "Discuss Prisma/Drizzle, OpenAPI/tRPC, schema validation with Pydantic/Zod, and caching layers.",
        },
        {
            "id": 2,
            "category": "problem_solving",
            "title": "WebSocket Scalability & Reconnection",
            "question": "You need to build a real-time collaborative feature for 100,000 concurrent connected users. How do you design the message broker, pub/sub architecture, and handle network disconnections?",
            "hint": "Mention Redis Pub/Sub, Kafka, WebSocket sticky sessions vs distributed brokers, and backoff reconnection.",
        },
        {
            "id": 3,
            "category": "behavioural",
            "title": "Prioritizing Tech Debt vs Deadlines",
            "question": "How do you navigate situations where business leadership demands an urgent launch date that requires cutting architectural corners? Give a concrete example.",
            "hint": "Use STAR format: explain pragmatic compromise, risk mitigation, and creating a formal tech-debt remediation milestone.",
        },
    ],
}


class InterviewEngineService:
    def get_questions_for_role(self, position: str) -> List[InterviewQuestionItem]:
        lowered = position.lower()
        matched_key = "backend"
        if any(w in lowered for w in ["front", "ui", "ux", "react", "next"]):
            matched_key = "frontend"
        elif any(w in lowered for w in ["ai", "ml", "data", "machine learning", "deep learning", "llm"]):
            matched_key = "ai_ml"
        elif any(w in lowered for w in ["full", "web", "software", "application"]):
            matched_key = "fullstack"
        elif any(w in lowered for w in ["back", "api", "cloud", "devops", "platform", "system"]):
            matched_key = "backend"

        raw_list = ROLE_QUESTION_PRESETS.get(matched_key, ROLE_QUESTION_PRESETS["backend"])

        questions: List[InterviewQuestionItem] = []
        for q in raw_list:
            questions.append(
                InterviewQuestionItem(
                    id=q["id"],
                    category=q["category"],
                    title=q["title"],
                    question=q["question"],
                    hint=q.get("hint"),
                )
            )
        return questions

    def evaluate_session(
        self,
        payload: InterviewEvaluateRequest,
        current_user: User,
        db: Session,
    ) -> InterviewSession:
        evaluation_data = self._run_evaluation(
            position=payload.position,
            answers=payload.answers,
            user_id=current_user.id,
            db=db,
        )

        overall = max(0, min(100, int(evaluation_data.get("overall_score", 70))))
        verdict = evaluation_data.get("verdict") or (
            "STRONG HIRE" if overall >= 85 else "HIRE" if overall >= 70 else "NEEDS WORK"
        )
        param_scores = evaluation_data.get("param_scores") or {
            "technical": overall,
            "problem_solving": overall,
            "behavioural": overall,
            "clarity": overall,
            "overall": overall,
        }
        param_scores["overall"] = overall

        qa_records: List[Dict[str, Any]] = []
        for ans in payload.answers:
            qa_records.append({
                "question_id": ans.question_id,
                "category": ans.category,
                "question": ans.question,
                "answer": ans.answer,
            })

        session_record = InterviewSession(
            user_id=current_user.id,
            position=payload.position.strip(),
            overall_score=overall,
            verdict=verdict,
            param_scores=param_scores,
            questions_and_answers=qa_records,
            strengths=evaluation_data.get("strengths", ["Clear communication", "Structured thinking"]),
            improvements=evaluation_data.get("improvements", ["Provide deeper trade-off analysis", "Add more quantifiable metrics"]),
        )
        db.add(session_record)
        db.commit()
        db.refresh(session_record)
        return session_record

    def _run_evaluation(
        self,
        position: str,
        answers: List[InterviewAnswerItem],
        user_id: str,
        db: Session,
    ) -> Dict[str, Any]:
        prompt_parts = [
            f"Candidate Target Position: {position}\n",
            "Evaluate the candidate's answers to the following 3 interview questions (1 technical, 1 problem-solving, 1 behavioural).\n",
        ]
        for idx, a in enumerate(answers, start=1):
            prompt_parts.append(
                f"Question {idx} [{a.category.upper()}]: {a.question}\nCandidate Answer: {a.answer if a.answer.strip() else '[No response provided]'}\n"
            )

        prompt_parts.append(
            "\nAnalyze depth, trade-off awareness, STAR structure in behavioural, and clarity. Return ONLY a valid JSON object matching this exact schema:\n"
            "{\n"
            '  "overall_score": <integer 0-100>,\n'
            '  "verdict": "<STRONG HIRE | HIRE | NEEDS WORK>",\n'
            '  "param_scores": {\n'
            '    "technical": <integer 0-100>,\n'
            '    "problem_solving": <integer 0-100>,\n'
            '    "behavioural": <integer 0-100>,\n'
            '    "clarity": <integer 0-100>\n'
            "  },\n"
            '  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],\n'
            '  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"]\n'
            "}"
        )

        full_prompt = "\n".join(prompt_parts)

        system_prompt = (
            "You are a Principal Engineering Director and Hiring Committee Chair conducting rigorous technical "
            "interviews. Score the candidate realistically based on technical competence, architectural trade-offs, "
            "and articulate delivery. Return ONLY valid JSON."
        )

        try:
            raw_response = llm_gateway.generate(
                prompt=full_prompt,
                system_prompt=system_prompt,
                json_mode=True,
                user_id=user_id,
                db=db,
            )
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)
            parsed = json.loads(cleaned)
            if "overall_score" in parsed and "param_scores" in parsed:
                return parsed
        except Exception as exc:
            logger.warning(f"BYOK LLM interview evaluation failed or unavailable: {exc}. Using deterministic NLP fallback.")

        return self._heuristic_evaluation(answers)

    def _heuristic_evaluation(self, answers: List[InterviewAnswerItem]) -> Dict[str, Any]:
        tech_score = 65
        problem_score = 65
        behaviour_score = 65
        clarity_score = 70

        tech_keywords = {
            "acid", "index", "cache", "redis", "concurrency", "lock", "thread",
            "asynchronous", "scale", "throughput", "latency", "replica", "api",
            "microservice", "docker", "kubernetes", "postgres", "sql", "http",
            "render", "bundle", "memo", "state", "rag", "embedding", "pipeline"
        }
        action_verbs = {"built", "architected", "resolved", "reduced", "led", "implemented", "optimized", "shipped"}

        for a in answers:
            ans_lower = a.answer.lower()
            words = ans_lower.split()
            word_count = len(words)

            if word_count < 10:
                bonus = -20
            elif word_count > 60:
                bonus = 15
            else:
                bonus = 5

            matched_kw = sum(1 for kw in tech_keywords if kw in ans_lower)
            matched_verbs = sum(1 for v in action_verbs if v in ans_lower)

            if a.category == "technical":
                tech_score = max(20, min(95, tech_score + bonus + (matched_kw * 4)))
            elif a.category == "problem_solving":
                problem_score = max(20, min(95, problem_score + bonus + (matched_kw * 3) + (matched_verbs * 3)))
            elif a.category == "behavioural":
                behaviour_score = max(20, min(95, behaviour_score + bonus + (matched_verbs * 5)))

            fillers = sum(ans_lower.count(f) for f in ["um", "uh", "like", "you know", "basically"])
            clarity_penalty = min(20, fillers * 4)
            clarity_score = max(40, min(95, clarity_score + (10 if word_count > 30 else 0) - clarity_penalty))

        overall = int((tech_score * 0.35) + (problem_score * 0.30) + (behaviour_score * 0.20) + (clarity_score * 0.15))
        verdict = "STRONG HIRE" if overall >= 85 else "HIRE" if overall >= 70 else "NEEDS WORK"

        return {
            "overall_score": overall,
            "verdict": verdict,
            "param_scores": {
                "technical": tech_score,
                "problem_solving": problem_score,
                "behavioural": behaviour_score,
                "clarity": clarity_score,
                "overall": overall,
            },
            "strengths": [
                "Demonstrated domain understanding of system bottlenecks and architecture.",
                "Clear structured narrative across problem breakdown.",
                "Good technical composure and relevant vocabulary.",
            ],
            "improvements": [
                "Quantify impact with concrete percentages, RPS, or latency metrics.",
                "Elaborate more deeply on edge case recovery and fallback mechanisms.",
                "Structure behavioural scenarios more tightly using the STAR framework.",
            ],
        }

    def get_latest_session(self, user_id: str, db: Session) -> Optional[InterviewSession]:
        return (
            db.query(InterviewSession)
            .filter(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .first()
        )

    def list_user_sessions(self, user_id: str, db: Session, limit: int = 10) -> List[InterviewSession]:
        return (
            db.query(InterviewSession)
            .filter(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .limit(limit)
            .all()
        )


interview_engine = InterviewEngineService()
