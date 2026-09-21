import json
from unittest.mock import patch
import pytest
from app.services.skill_normalizer import normalize_skill


@pytest.fixture
def auth_header_sg(client):
    email = "sguser@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "SG User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_skill_normalizer():
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("ECMAScript") == "JavaScript"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("docker") == "Docker"
    assert normalize_skill("fastapi") == "FastAPI"


def test_compare_student_to_job_with_smart_suggestions(client, auth_header_sg):
    client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "Languages", "proficiency": "Advanced"},
        headers=auth_header_sg,
    )
    client.post(
        "/api/v1/profile/projects",
        json={"title": "Cloud Resume", "technologies": ["Python", "FastAPI"]},
        headers=auth_header_sg,
    )

    search_resp = client.post(
        "/api/v1/jobs/search",
        json={"role": "Backend Engineer", "limit": 1},
        headers=auth_header_sg,
    )
    jobs = search_resp.json()["jobs"]
    assert len(jobs) >= 1
    job_id = jobs[0]["id"]

    mock_llm_suggestions = json.dumps({
        "improvement_explanation": "You have a strong Python foundation, but lack Docker and AWS evidence required for this role.",
        "smart_suggestions": [
            {
                "type": "PROJECT_ENHANCEMENT",
                "title": "Containerize 'Cloud Resume' with Docker",
                "action": "Add a production Dockerfile and docker-compose to 'Cloud Resume'.",
                "impact": "Directly proves Docker competency.",
            },
            {
                "type": "DSA_PRACTICE",
                "title": "Practice Graph Algorithms",
                "action": "Focus on BFS/DFS traversals.",
                "impact": "Critical for technical round 1.",
            },
            {
                "type": "STACK_EXPANSION",
                "title": "Learn AWS Core Services",
                "action": "Deploy on AWS ECS or Lambda.",
                "impact": "Fulfills cloud deployment requirement.",
            },
        ],
    })

    with patch("app.services.llm_gateway.llm_gateway.generate", return_value=mock_llm_suggestions):
        compare_resp = client.post(
            f"/api/v1/jobs/{job_id}/compare",
            headers=auth_header_sg,
        )
        assert compare_resp.status_code == 200
        match_data = compare_resp.json()
        assert "match_score" in match_data
        assert isinstance(match_data["match_score"], (int, float))
        assert "improvement_explanation" in match_data
        assert len(match_data["smart_suggestions"]) >= 1
        assert match_data["smart_suggestions"][0]["type"] in {
            "PROJECT_ENHANCEMENT", "DSA_PRACTICE", "STACK_EXPANSION", "RESUME_OPTIMIZATION"
        }

        get_match = client.get(
            f"/api/v1/jobs/{job_id}/match",
            headers=auth_header_sg,
        )
        assert get_match.status_code == 200
        assert get_match.json()["id"] == match_data["id"]
