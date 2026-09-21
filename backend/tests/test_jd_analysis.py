import json
from unittest.mock import patch
import pytest
from app.services.jd_analyzer import clean_jd_text, parse_and_validate_llm_json


@pytest.fixture
def auth_header_jda(client):
    email = "jdauser@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "JDA User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_clean_jd_text():
    dirty = "<div><h1>Backend Engineer</h1><p>We need Python &amp; FastAPI developers.&nbsp;</p></div>\n\n\n\nMust have 2+ years."
    cleaned = clean_jd_text(dirty)
    assert "<div>" not in cleaned
    assert "Backend Engineer" in cleaned
    assert "Python" in cleaned
    assert "\n\n\n" not in cleaned


def test_parse_and_validate_llm_json():
    fenced_json = """```json
    {
      "role": "Senior Cloud Architect",
      "required_skills": ["AWS", "Terraform"],
      "preferred_skills": ["Kubernetes"],
      "education_requirements": ["B.Tech"],
      "experience_requirements": ["5+ years"],
      "responsibilities": ["Lead cloud migration"],
      "tools": ["Docker"],
      "interview_topics": ["Distributed Systems"]
    }
    ```"""
    parsed = parse_and_validate_llm_json(fenced_json)
    assert parsed.role == "Senior Cloud Architect"
    assert "AWS" in parsed.required_skills
    assert "Kubernetes" in parsed.preferred_skills


def test_analyze_job_description_caching(client, auth_header_jda):
    mock_llm_response = json.dumps({
        "role": "Full Stack Engineer",
        "required_skills": ["Python", "React"],
        "preferred_skills": ["Docker"],
        "education_requirements": ["Bachelor's in CS"],
        "experience_requirements": ["Fresher to 1 year"],
        "responsibilities": ["Build web applications"],
        "tools": ["VS Code", "Git"],
        "interview_topics": ["Data Structures", "Web Dev"],
    })

    with patch("app.services.llm_gateway.llm_gateway.generate", return_value=mock_llm_response):
        payload = {
            "raw_jd": "Full Stack Engineer needed with Python and React skills. Freshers welcome.",
            "force_refresh": False,
        }

        resp1 = client.post("/api/v1/jobs/analyze", json=payload, headers=auth_header_jda)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["cached"] is False
        assert data1["role"] == "Full Stack Engineer"
        assert "Python" in data1["required_skills"]

        resp2 = client.post("/api/v1/jobs/analyze", json=payload, headers=auth_header_jda)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["cached"] is True
        assert data2["id"] == data1["id"]
