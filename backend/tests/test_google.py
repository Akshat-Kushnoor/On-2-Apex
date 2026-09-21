from datetime import datetime, timedelta, timezone
import pytest


@pytest.fixture
def auth_header_google(client):
    email = "google_user@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Google User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_google_auth_flow(client, auth_header_google):
    url_resp = client.get(
        "/api/v1/google/auth-url",
        headers=auth_header_google,
    )
    assert url_resp.status_code == 200
    assert "auth_url" in url_resp.json()

    status_resp = client.get(
        "/api/v1/google/status",
        headers=auth_header_google,
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["connected"] is False

    cb_resp = client.get(
        "/api/v1/google/oauth2/callback?code=mock_code_12345",
        headers=auth_header_google,
    )
    assert cb_resp.status_code == 200
    cb_data = cb_resp.json()
    assert cb_data["connected"] is True
    assert len(cb_data["scopes"]) >= 2

    post_status = client.get(
        "/api/v1/google/status",
        headers=auth_header_google,
    )
    assert post_status.status_code == 200
    assert post_status.json()["connected"] is True

    disc_resp = client.delete(
        "/api/v1/google/disconnect",
        headers=auth_header_google,
    )
    assert disc_resp.status_code == 204

    after_disc = client.get(
        "/api/v1/google/status",
        headers=auth_header_google,
    )
    assert after_disc.status_code == 200
    assert after_disc.json()["connected"] is False


def test_google_calendar_sync_application(client, auth_header_google):
    deadline_date = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    app_resp = client.post(
        "/api/v1/workspace/applications",
        json={
            "company": "Amazon",
            "role": "SDE 1",
            "stage": "APPLIED",
            "deadline": deadline_date,
        },
        headers=auth_header_google,
    )
    app_id = app_resp.json()["id"]

    interview_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    client.post(
        f"/api/v1/workspace/applications/{app_id}/events",
        json={
            "event_type": "INTERVIEW_SCHEDULED",
            "title": "Amazon Bar Raiser Screen",
            "event_date": interview_date,
        },
        headers=auth_header_google,
    )

    sync_resp = client.post(
        f"/api/v1/google/calendar/sync-application/{app_id}",
        headers=auth_header_google,
    )
    assert sync_resp.status_code == 200
    sync_data = sync_resp.json()
    assert sync_data["synced_events_count"] >= 1
    assert len(sync_data["event_ids"]) >= 1


def test_google_calendar_sync_learning_task(client, auth_header_google):
    search_resp = client.post(
        "/api/v1/jobs/search",
        json={"role": "Backend Engineer", "limit": 1},
        headers=auth_header_google,
    )
    job_id = search_resp.json()["jobs"][0]["id"]

    plan_resp = client.post(
        "/api/v1/learning/plan",
        json={"job_id": job_id, "hours_per_week": 8, "target_weeks": 2},
        headers=auth_header_google,
    )
    task_id = plan_resp.json()["tasks"][0]["id"]

    task_sync = client.post(
        f"/api/v1/google/calendar/sync-task/{task_id}",
        json={"duration_hours": 2.5},
        headers=auth_header_google,
    )
    assert task_sync.status_code == 200
    assert task_sync.json()["synced_events_count"] == 1


def test_gmail_scan_proposals(client, auth_header_google):
    client.post(
        "/api/v1/workspace/applications",
        json={
            "company": "Figma",
            "role": "Frontend Systems Engineer",
            "stage": "APPLIED",
        },
        headers=auth_header_google,
    )

    scan_resp = client.post(
        "/api/v1/google/gmail/scan",
        headers=auth_header_google,
    )
    assert scan_resp.status_code == 200
    data = scan_resp.json()
    assert data["scanned_count"] >= 1
    assert len(data["matches"]) >= 1
    assert data["matches"][0]["company"] == "Figma"
    assert "suggested_action" in data["matches"][0]
