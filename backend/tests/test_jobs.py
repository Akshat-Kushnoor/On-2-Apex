import pytest
from app.services.job_normalizer import (
    calculate_dedup_hash,
    canonicalize_url,
    normalize_company,
    normalize_title,
)


@pytest.fixture
def auth_header(client):
    email = "jobseeker@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Job Seeker"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_company_normalization():
    assert normalize_company("Google LLC") == "Google"
    assert normalize_company("google") == "Google"
    assert normalize_company("Microsoft Corporation") == "Microsoft"
    assert normalize_company("Acme Technologies Pvt Ltd") == "Acme"


def test_title_normalization():
    assert normalize_title("Senior Software Engineer (m/f/d)") == "Senior Software Engineer"
    assert normalize_title("Hiring for Full Stack Developer") == "Full Stack Developer"
    assert normalize_title("[Urgent] Python Developer") == "Python Developer"


def test_url_canonicalization():
    url1 = "https://example.com/jobs/123?utm_source=linkedin&ref=board"
    assert canonicalize_url(url1) == "https://example.com/jobs/123"

    url2 = "https://example.com/jobs/123/"
    assert canonicalize_url(url2) == "https://example.com/jobs/123"


def test_dedup_hash_consistency():
    hash1 = calculate_dedup_hash("Google", "Software Engineer", "https://google.com/jobs/1")
    hash2 = calculate_dedup_hash("google", "software engineer", "https://google.com/jobs/1")
    assert hash1 == hash2


def test_job_search_and_persistence(client, auth_header):
    payload = {
        "role": "Software Engineer",
        "location": "Bengaluru",
        "keywords": ["Python", "FastAPI"],
        "limit": 5,
    }
    resp = client.post("/api/v1/jobs/search", json=payload, headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_found"] >= 1
    assert len(data["jobs"]) >= 1
    job = data["jobs"][0]
    assert "id" in job
    assert "company" in job
    assert "skills" in job


def test_job_list_and_filter(client, auth_header):
    resp = client.get("/api/v1/jobs?limit=10", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1


def test_save_and_unsave_job(client, auth_header):
    list_resp = client.get("/api/v1/jobs?limit=1", headers=auth_header)
    job_id = list_resp.json()["items"][0]["id"]

    save_resp = client.post(f"/api/v1/jobs/{job_id}/save", headers=auth_header)
    assert save_resp.status_code == 200

    saved_resp = client.get("/api/v1/jobs/saved", headers=auth_header)
    assert saved_resp.status_code == 200
    assert any(j["id"] == job_id for j in saved_resp.json())

    unsave_resp = client.delete(f"/api/v1/jobs/{job_id}/save", headers=auth_header)
    assert unsave_resp.status_code == 200

    saved_after = client.get("/api/v1/jobs/saved", headers=auth_header)
    assert not any(j["id"] == job_id for j in saved_after.json())
