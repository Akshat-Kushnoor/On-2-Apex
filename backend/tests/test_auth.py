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


def test_get_me_authenticated(client):
    # 1. Login to get token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "student1@example.com", "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]

    # 2. Query /me with token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "student1@example.com"
    assert me_data["full_name"] == "Test Student 1"
    assert me_data["is_active"] is True


def test_protected_route_rejects_missing_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"
