from datetime import datetime, timedelta, timezone
import pytest


@pytest.fixture
def auth_header_workspace(client):
    email = "workspace_user@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Workspace User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_other(client):
    email = "other_user@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Other User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_workspace_application_lifecycle(client, auth_header_workspace):
    deadline_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    create_resp = client.post(
        "/api/v1/workspace/applications",
        json={
            "company": "Stripe",
            "role": "Backend Engineer",
            "stage": "WISHLIST",
            "salary": "$140k - $160k",
            "location": "Remote, US",
            "notes": "Applied via referral link.",
            "deadline": deadline_date,
        },
        headers=auth_header_workspace,
    )
    assert create_resp.status_code == 201
    app_data = create_resp.json()
    app_id = app_data["id"]
    assert app_data["company"] == "Stripe"
    assert app_data["stage"] == "WISHLIST"
    assert len(app_data["events"]) == 1
    assert app_data["events"][0]["event_type"] == "STAGE_CHANGE"

    board_resp = client.get(
        "/api/v1/workspace/board",
        headers=auth_header_workspace,
    )
    assert board_resp.status_code == 200
    board_data = board_resp.json()
    assert board_data["total_applications"] >= 1
    assert any(a["id"] == app_id for a in board_data["stages"]["wishlist"])

    stage_resp = client.post if False else client.put(
        f"/api/v1/workspace/applications/{app_id}/stage",
        json={"stage": "APPLIED", "note": "Referral officially submitted."},
        headers=auth_header_workspace,
    )
    assert stage_resp.status_code == 200
    updated_app = stage_resp.json()
    assert updated_app["stage"] == "APPLIED"
    assert updated_app["applied_at"] is not None
    assert len(updated_app["events"]) == 2

    interview_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    event_resp = client.post(
        f"/api/v1/workspace/applications/{app_id}/events",
        json={
            "event_type": "INTERVIEW_SCHEDULED",
            "title": "Technical Screen Round 1",
            "description": "DSA and System Design discussion with Engineering Manager.",
            "event_date": interview_date,
        },
        headers=auth_header_workspace,
    )
    assert event_resp.status_code == 201
    event_data = event_resp.json()
    assert event_data["title"] == "Technical Screen Round 1"

    upcoming_resp = client.get(
        "/api/v1/workspace/upcoming?days_ahead=14",
        headers=auth_header_workspace,
    )
    assert upcoming_resp.status_code == 200
    upcoming = upcoming_resp.json()
    assert len(upcoming) >= 1
    assert any(u["application_id"] == app_id for u in upcoming)

    list_resp = client.get(
        "/api/v1/workspace/applications?stage=APPLIED",
        headers=auth_header_workspace,
    )
    assert list_resp.status_code == 200
    assert any(a["id"] == app_id for a in list_resp.json())

    update_resp = client.put(
        f"/api/v1/workspace/applications/{app_id}",
        json={"salary": "$150k - $170k", "notes": "Updated salary expectations."},
        headers=auth_header_workspace,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["salary"] == "$150k - $170k"

    del_resp = client.delete(
        f"/api/v1/workspace/applications/{app_id}",
        headers=auth_header_workspace,
    )
    assert del_resp.status_code == 204

    get_del = client.get(
        f"/api/v1/workspace/applications/{app_id}",
        headers=auth_header_workspace,
    )
    assert get_del.status_code == 404


def test_workspace_isolation(client, auth_header_workspace, auth_header_other):
    create_resp = client.post(
        "/api/v1/workspace/applications",
        json={"company": "PrivateCorp", "role": "Security Engineer", "stage": "WISHLIST"},
        headers=auth_header_workspace,
    )
    assert create_resp.status_code == 201
    app_id = create_resp.json()["id"]

    other_get = client.get(
        f"/api/v1/workspace/applications/{app_id}",
        headers=auth_header_other,
    )
    assert other_get.status_code == 404

    other_update = client.put(
        f"/api/v1/workspace/applications/{app_id}/stage",
        json={"stage": "REJECTED"},
        headers=auth_header_other,
    )
    assert other_update.status_code == 404
