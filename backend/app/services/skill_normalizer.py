import re
from typing import Dict, List, Set

CANONICAL_SKILLS_MAP: Dict[str, str] = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ecmascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express",
    "expressjs": "Express",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "pgsql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sql": "SQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "git": "Git",
    "github": "Git",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "restful": "REST APIs",
    "graphql": "GraphQL",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "java": "Java",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "system design": "System Design",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
}


def normalize_skill(skill: str) -> str:
    if not skill:
        return ""
    cleaned = skill.strip().lower()
    cleaned = re.sub(r"[\(\)\[\],]", "", cleaned).strip()
    return CANONICAL_SKILLS_MAP.get(cleaned, skill.strip())


def get_canonical_skill_set(skills: List[str]) -> Set[str]:
    result = set()
    for s in skills:
        norm = normalize_skill(s)
        if norm:
            result.add(norm)
    return result
