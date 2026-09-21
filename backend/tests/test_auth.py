def test_register_user_success(client):
    payload = {
        "email": "student1@example.com",
        "password": "Password123!",
        "full_name": "Test Student 1",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "student1@example.com"
    assert data["user"]["full_name"] == "Test Student 1"


def test_register_duplicate_email_fails(client):
    payload = {
        "email": "student1@example.com",
        "password": "Password123!",
        "full_name": "Test Student 1 Duplicate",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_login_success(client):
    payload = {
        "email": "student1@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "student1@example.com"


def test_login_invalid_password_fails(client):
    payload = {
        "email": "student1@example.com",
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_email_fails(client):
    payload = {
        "email": "nobody@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_password_reset_flow(client):
    # 1. Request password reset
    reset_req = client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": "student1@example.com"},
    )
    assert reset_req.status_code == 200
    req_data = reset_req.json()
    assert "reset_token" in req_data
    reset_token = req_data["reset_token"]

    # 2. Confirm reset with new password
    confirm_resp = client.post(
        "/api/v1/auth/password-reset",
        json={"token": reset_token, "new_password": "NewSecurePassword456!"},
    )
    assert confirm_resp.status_code == 200
    assert "Password updated" in confirm_resp.json()["message"]

    # 3. Old password should now fail
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "student1@example.com", "password": "Password123!"},
    )
    assert old_login.status_code == 400

    # 4. New password should succeed
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "student1@example.com", "password": "NewSecurePassword456!"},
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()


def test_password_reset_invalid_token_fails(client):
    resp = client.post(
        "/api/v1/auth/password-reset",
        json={"token": "invalid_fake_token_value", "new_password": "NewPassword123!"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


def test_google_social_auth_login_and_register(client):
    # 1. First time Google login creates user
    google_payload = {
        "provider": "google",
        "email": "google.student@university.edu",
        "full_name": "Google Student",
        "access_token": "mock_google_token_12345",
    }
    resp1 = client.post("/api/v1/auth/google", json=google_payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "access_token" in data1
    assert data1["user"]["email"] == "google.student@university.edu"
    assert data1["user"]["full_name"] == "Google Student"

    # 2. Subsequent Google login logs in existing user
    resp2 = client.post("/api/v1/auth/google", json=google_payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "access_token" in data2
    assert data2["user"]["id"] == data1["user"]["id"]


def test_github_social_auth_login_and_register(client):
    # 1. First time GitHub login creates user
    github_payload = {
        "provider": "github",
        "email": "github.developer@university.edu",
        "full_name": "GitHub Developer",
        "access_token": "mock_github_token_67890",
    }
    resp1 = client.post("/api/v1/auth/github", json=github_payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "access_token" in data1
    assert data1["user"]["email"] == "github.developer@university.edu"
    assert data1["user"]["full_name"] == "GitHub Developer"

    # 2. Subsequent GitHub login logs in existing user
    resp2 = client.post("/api/v1/auth/github", json=github_payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "access_token" in data2
    assert data2["user"]["id"] == data1["user"]["id"]


def test_oauth_url_generation(client):
    # Google URL
    g_res = client.get("/api/v1/auth/oauth/google/url")
    assert g_res.status_code == 200
    assert g_res.json()["provider"] == "google"
    assert "auth_url" in g_res.json()

    # GitHub URL
    gh_res = client.get("/api/v1/auth/oauth/github/url")
    assert gh_res.status_code == 200
    assert gh_res.json()["provider"] == "github"
    assert "auth_url" in gh_res.json()


def test_oauth_code_callback_exchange(client):
    # Callback exchange with mock code
    callback_payload = {
        "provider": "google",
        "code": "mock_code_test_user",
    }
    resp = client.post("/api/v1/auth/oauth/callback", json=callback_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "google.user" in data["user"]["email"]


def test_get_me_authenticated(client):
    # 1. Social login to get token
    login_resp = client.post(
        "/api/v1/auth/google",
        json={
            "provider": "google",
            "email": "profile.check@example.com",
            "full_name": "Profile Check User",
        },
    )
    token = login_resp.json()["access_token"]

    # 2. Query /me with token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "profile.check@example.com"
    assert me_data["full_name"] == "Profile Check User"
    assert me_data["is_active"] is True


def test_protected_route_rejects_missing_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"
