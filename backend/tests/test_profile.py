import pytest


@pytest.fixture
def auth_header_user_a(client):
    email = "usera@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "User Alpha"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_user_b(client):
    email = "userb@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "User Beta"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_and_update_profile(client, auth_header_user_a):
    # 1. Get initial profile
    resp = client.get("/api/v1/profile", headers=auth_header_user_a)
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "User Alpha"
    assert data["skills"] == []

    # 2. Update base profile
    update_payload = {
        "college": "Apex Institute of Technology",
        "degree": "B.Tech",
        "branch": "Computer Science",
        "graduation_year": 2026,
        "cgpa": 8.95,
        "preferred_roles": ["Full Stack Engineer", "Backend Developer"],
        "preferred_locations": ["Bengaluru", "Remote"],
    }
    put_resp = client.put("/api/v1/profile", json=update_payload, headers=auth_header_user_a)
    assert put_resp.status_code == 200
    profile_data = put_resp.json()
    assert profile_data["college"] == "Apex Institute of Technology"
    assert profile_data["cgpa"] == 8.95
    assert "Full Stack Engineer" in profile_data["preferred_roles"]


def test_skills_crud(client, auth_header_user_a):
    # Add skill
    skill_payload = {
        "name": "Python",
        "category": "Programming Languages",
        "proficiency": "Advanced",
        "evidence": "Built multiple FastAPI services and microservices",
    }
    post_resp = client.post("/api/v1/profile/skills", json=skill_payload, headers=auth_header_user_a)
    assert post_resp.status_code == 201
    skill = post_resp.json()
    assert skill["name"] == "Python"
    skill_id = skill["id"]

    # List skills
    list_resp = client.get("/api/v1/profile/skills", headers=auth_header_user_a)
    assert list_resp.status_code == 200
    skills = list_resp.json()
    assert any(s["id"] == skill_id for s in skills)

    # Delete skill
    del_resp = client.delete(f"/api/v1/profile/skills/{skill_id}", headers=auth_header_user_a)
    assert del_resp.status_code == 200

    # Verify deleted
    list_after = client.get("/api/v1/profile/skills", headers=auth_header_user_a).json()
    assert not any(s["id"] == skill_id for s in list_after)


def test_projects_crud(client, auth_header_user_a):
    # Add project
    proj_payload = {
        "title": "Placement OS",
        "description": "AI placement coach platform",
        "technologies": ["Python", "FastAPI", "Next.js", "SQLite"],
        "role": "Lead Engineer",
        "repo_url": "https://github.com/example/placement-os",
    }
    post_resp = client.post("/api/v1/profile/projects", json=proj_payload, headers=auth_header_user_a)
    assert post_resp.status_code == 201
    project = post_resp.json()
    project_id = project["id"]
    assert project["title"] == "Placement OS"

    # Update project
    update_payload = {"role": "Principal Architect"}
    put_resp = client.put(f"/api/v1/profile/projects/{project_id}", json=update_payload, headers=auth_header_user_a)
    assert put_resp.status_code == 200
    assert put_resp.json()["role"] == "Principal Architect"

    # List projects
    list_resp = client.get("/api/v1/profile/projects", headers=auth_header_user_a)
    assert any(p["id"] == project_id for p in list_resp.json())

    # Delete project
    del_resp = client.delete(f"/api/v1/profile/projects/{project_id}", headers=auth_header_user_a)
    assert del_resp.status_code == 200


def test_cross_tenant_ownership_isolation(client, auth_header_user_a, auth_header_user_b):
    """Verifies that User B cannot read or mutate User A's profile sub-resources."""
    # User A creates a skill and project
    skill_resp = client.post(
        "/api/v1/profile/skills",
        json={"name": "Rust", "category": "Languages", "proficiency": "Intermediate"},
        headers=auth_header_user_a,
    )
    skill_a_id = skill_resp.json()["id"]

    project_resp = client.post(
        "/api/v1/profile/projects",
        json={"title": "Alpha Secret Project", "technologies": ["Rust"]},
        headers=auth_header_user_a,
    )
    project_a_id = project_resp.json()["id"]

    # 1. User B tries to delete User A's skill -> should receive 404 NOT_FOUND
    del_skill_resp = client.delete(f"/api/v1/profile/skills/{skill_a_id}", headers=auth_header_user_b)
    assert del_skill_resp.status_code == 404
    assert del_skill_resp.json()["error"]["code"] == "NOT_FOUND"

    # 2. User B tries to update User A's project -> should receive 404 NOT_FOUND
    put_proj_resp = client.put(
        f"/api/v1/profile/projects/{project_a_id}",
        json={"title": "Hacked Title"},
        headers=auth_header_user_b,
    )
    assert put_proj_resp.status_code == 404

    # 3. User B gets their full profile -> must NOT contain User A's skill or project
    user_b_profile = client.get("/api/v1/profile", headers=auth_header_user_b).json()
    assert not any(s["id"] == skill_a_id for s in user_b_profile["skills"])
    assert not any(p["id"] == project_a_id for p in user_b_profile["projects"])
