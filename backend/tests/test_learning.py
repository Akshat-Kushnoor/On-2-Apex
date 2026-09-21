import json
from unittest.mock import patch
import pytest


@pytest.fixture
def auth_header_learning(client):
    email = "learning_user@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Learning User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_manage_learning_plan(client, auth_header_learning):
    client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "Languages", "proficiency": "Intermediate"},
        headers=auth_header_learning,
    )
    client.post(
        "/api/v1/profile/projects",
        json={"title": "Task Orchestrator", "technologies": ["Python", "FastAPI"]},
        headers=auth_header_learning,
    )

    search_resp = client.post(
        "/api/v1/jobs/search",
        json={"role": "Backend Engineer", "limit": 1},
        headers=auth_header_learning,
    )
    job_id = search_resp.json()["jobs"][0]["id"]

    mock_llm_plan = json.dumps({
        "tasks": [
            {
                "skill": "Docker",
                "title": "Master Docker Containerization",
                "description": "Learn container lifecycle and multi-stage builds.",
                "week_number": 1,
                "priority": "HIGH",
                "estimated_hours": 5.0,
                "learning_goal": "Containerize backend apps",
                "topics": ["Dockerfiles", "Networking", "Volumes"],
                "practice_project": "Containerize Task Orchestrator",
                "interview_question_prep": "Explain container vs VM and layer caching.",
            },
            {
                "skill": "Kubernetes",
                "title": "Deploy to Kubernetes Cluster",
                "description": "Learn Pods, Deployments, and Services.",
                "week_number": 2,
                "priority": "HIGH",
                "estimated_hours": 5.0,
                "learning_goal": "Deploy app to local minikube",
                "topics": ["Pods", "Services", "Deployments"],
                "practice_project": "Create K8s manifests for Task Orchestrator",
                "interview_question_prep": "Difference between ClusterIP and NodePort.",
            },
        ]
    })

    with patch("app.services.llm_gateway.llm_gateway.generate", return_value=mock_llm_plan):
        plan_resp = client.post(
            "/api/v1/learning/plan",
            json={
                "job_id": job_id,
                "hours_per_week": 10,
                "target_weeks": 2,
            },
            headers=auth_header_learning,
        )
        assert plan_resp.status_code == 201
        plan_data = plan_resp.json()
        assert plan_data["status"] == "ACTIVE"
        assert plan_data["hours_per_week"] == 10
        assert plan_data["total_weeks"] == 2
        assert len(plan_data["tasks"]) == 2
        assert plan_data["progress_pct"] == 0.0

        plan_id = plan_data["id"]
        first_task = plan_data["tasks"][0]
        task_id = first_task["id"]

        active_resp = client.get(
            "/api/v1/learning/plan/active",
            headers=auth_header_learning,
        )
        assert active_resp.status_code == 200
        assert active_resp.json()["id"] == plan_id

        get_by_id_resp = client.get(
            f"/api/v1/learning/plan/{plan_id}",
            headers=auth_header_learning,
        )
        assert get_by_id_resp.status_code == 200
        assert get_by_id_resp.json()["id"] == plan_id

        all_plans_resp = client.get(
            "/api/v1/learning/plans",
            headers=auth_header_learning,
        )
        assert all_plans_resp.status_code == 200
        assert len(all_plans_resp.json()) >= 1

        update_task_resp = client.put(
            f"/api/v1/learning/tasks/{task_id}",
            json={
                "status": "COMPLETED",
                "evidence": "https://github.com/example/repo/pull/1",
            },
            headers=auth_header_learning,
        )
        assert update_task_resp.status_code == 200
        updated_task = update_task_resp.json()
        assert updated_task["status"] == "COMPLETED"
        assert updated_task["evidence"] == "https://github.com/example/repo/pull/1"
        assert updated_task["completed_at"] is not None

        refreshed_active = client.get(
            "/api/v1/learning/plan/active",
            headers=auth_header_learning,
        )
        assert refreshed_active.status_code == 200
        refreshed_data = refreshed_active.json()
        assert refreshed_data["completed_hours"] == 5.0
        assert refreshed_data["progress_pct"] == 50.0


def test_learning_plan_fallback(client, auth_header_learning):
    search_resp = client.post(
        "/api/v1/jobs/search",
        json={"role": "Software Engineer", "limit": 1},
        headers=auth_header_learning,
    )
    job_id = search_resp.json()["jobs"][0]["id"]

    with patch("app.services.llm_gateway.llm_gateway.generate", side_effect=Exception("LLM down")):
        fallback_resp = client.post(
            "/api/v1/learning/plan",
            json={
                "job_id": job_id,
                "hours_per_week": 8,
                "target_weeks": 2,
            },
            headers=auth_header_learning,
        )
        assert fallback_resp.status_code == 201
        plan_data = fallback_resp.json()
        assert len(plan_data["tasks"]) == 4
        assert plan_data["status"] == "ACTIVE"


def test_learning_plan_not_found(client, auth_header_learning):
    bad_plan_resp = client.get(
        "/api/v1/learning/plan/nonexistent-id",
        headers=auth_header_learning,
    )
    assert bad_plan_resp.status_code == 404

    bad_task_resp = client.put(
        "/api/v1/learning/tasks/nonexistent-task-id",
        json={"status": "IN_PROGRESS"},
        headers=auth_header_learning,
    )
    assert bad_task_resp.status_code == 404
