import json
from unittest.mock import patch
import pytest


@pytest.fixture
def auth_header_resume(client):
    email = "resume_user@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Resume User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_resume_generation_lifecycle(client, auth_header_resume):
    client.post(
        "/api/v1/profile/skills",
        json={"name": "FastAPI", "category": "Frameworks", "proficiency": "Advanced"},
        headers=auth_header_resume,
    )
    client.post(
        "/api/v1/profile/projects",
        json={"title": "E-Commerce Gateway", "technologies": ["Python", "FastAPI", "PostgreSQL"], "description": "Built high scale API gateway."},
        headers=auth_header_resume,
    )

    search_resp = client.post(
        "/api/v1/jobs/search",
        json={"role": "Backend Engineer", "limit": 1},
        headers=auth_header_resume,
    )
    job = search_resp.json()["jobs"][0]
    job_id = job["id"]
    job_company = job.get("company", "TechCorp")

    mock_llm_output = json.dumps({
        "position": "Backend Engineer",
        "tags": ["Backend Engineer", "API Engineer", "Python Developer"],
        "projects": [
            {
                "id": "proj_1",
                "title": "E-Commerce Gateway",
                "bullets": [
                    "Accomplished 35% latency reduction by optimizing FastAPI connection pooling and indexing PostgreSQL queries."
                ],
                "explanation": "Quantified impact and emphasized PostgreSQL and FastAPI alignment.",
                "keywords_added": ["latency", "PostgreSQL", "FastAPI"],
            }
        ],
        "experiences": []
    })

    with patch("app.services.llm_gateway.llm_gateway.generate", return_value=mock_llm_output):
        gen_resp = client.post(
            "/api/v1/resumes/generate",
            json={
                "job_id": job_id,
                "custom_position": "Backend Engineer",
                "custom_instructions": "Highlight performance metrics.",
            },
            headers=auth_header_resume,
        )
        assert gen_resp.status_code == 201
        resume_data = gen_resp.json()

        assert resume_data["position"] == "Backend Engineer"
        assert "Backend Engineer" in resume_data["tags"]
        assert job_company in resume_data["applied_companies"]
        assert len(resume_data["diffs"]) >= 1
        assert "latency" in resume_data["diffs"][0]["keywords_added"]
        assert len(resume_data["markdown"]) > 0
        assert r"\documentclass" in resume_data["latex"]

        resume_id = resume_data["id"]

        list_resp = client.get(
            "/api/v1/resumes",
            headers=auth_header_resume,
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        filter_resp = client.get(
            "/api/v1/resumes?tag=Backend",
            headers=auth_header_resume,
        )
        assert filter_resp.status_code == 200
        assert len(filter_resp.json()) >= 1

        get_resp = client.get(
            f"/api/v1/resumes/{resume_id}",
            headers=auth_header_resume,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == resume_id

        md_resp = client.get(
            f"/api/v1/resumes/{resume_id}/markdown",
            headers=auth_header_resume,
        )
        assert md_resp.status_code == 200
        assert "Resume User" in md_resp.text or "Candidate" in md_resp.text

        tex_resp = client.get(
            f"/api/v1/resumes/{resume_id}/latex",
            headers=auth_header_resume,
        )
        assert tex_resp.status_code == 200
        assert r"\begin{document}" in tex_resp.text

        apply_resp = client.post(
            f"/api/v1/resumes/{resume_id}/apply",
            json={"company_name": "Google"},
            headers=auth_header_resume,
        )
        assert apply_resp.status_code == 200
        assert "Google" in apply_resp.json()["applied_companies"]

        update_resp = client.put(
            f"/api/v1/resumes/{resume_id}",
            json={"status": "FINALIZED"},
            headers=auth_header_resume,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "FINALIZED"

        del_resp = client.delete(
            f"/api/v1/resumes/{resume_id}",
            headers=auth_header_resume,
        )
        assert del_resp.status_code == 204


def test_resume_fallback_when_llm_offline(client, auth_header_resume):
    search_resp = client.post(
        "/api/v1/jobs/search",
        json={"role": "Full Stack Developer", "limit": 1},
        headers=auth_header_resume,
    )
    job_id = search_resp.json()["jobs"][0]["id"]

    with patch("app.services.llm_gateway.llm_gateway.generate", side_effect=Exception("LLM offline")):
        fb_resp = client.post(
            "/api/v1/resumes/generate",
            json={"job_id": job_id},
            headers=auth_header_resume,
        )
        assert fb_resp.status_code == 201
        data = fb_resp.json()
        assert len(data["tags"]) >= 1
        assert len(data["markdown"]) > 0
        assert len(data["latex"]) > 0
