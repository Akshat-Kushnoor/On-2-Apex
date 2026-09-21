import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_auth_tests():
    print("=" * 60)
    print("STARTING FULL AUTHENTICATION & RECOVERY TEST SUITE")
    print("=" * 60)

    unique_id = uuid.uuid4().hex[:6]
    test_email = f"alex.{unique_id}@apex.edu"

    # 1. Register with Email/Password
    print(f"\n[TEST 1] Registering new user with email & password ({test_email})...")
    reg_payload = {
        "email": test_email,
        "password": "ApexPassword123!",
        "full_name": "Alex Student",
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    print(f"Status: {res.status_code}")
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    data = res.json()
    token = data["access_token"]
    assert token, "Token should exist"
    print(f"[OK] Registered: {data['user']['email']} (Token: {token[:20]}...)")

    # 2. Login with Email/Password
    print("\n[TEST 2] Logging in with email & password...")
    login_payload = {
        "email": test_email,
        "password": "ApexPassword123!",
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    print(f"[OK] Login successful: {res.json()['user']['email']}")

    # 3. Password Reset Request & Confirm
    print("\n[TEST 3] Requesting password reset...")
    reset_req = client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": test_email},
    )
    assert reset_req.status_code == 200
    reset_token = reset_req.json().get("reset_token")
    assert reset_token, "Reset token generated"
    print(f"[OK] Reset token generated: {reset_token[:20]}...")

    print("\n[TEST 4] Confirming password reset with new password...")
    confirm_res = client.post(
        "/api/v1/auth/password-reset",
        json={"token": reset_token, "new_password": "NewApexPassword999!"},
    )
    assert confirm_res.status_code == 200
    print(f"[OK] Password reset confirmed: {confirm_res.json()['message']}")

    # 4. Verify Old Password Fails and New Password Succeeds
    print("\n[TEST 5] Testing old password rejected & new password accepted...")
    old_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": "ApexPassword123!"},
    )
    assert old_res.status_code == 400
    print("[OK] Old password correctly rejected (400)")

    new_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": "NewApexPassword999!"},
    )
    assert new_res.status_code == 200
    print("[OK] New password login successful (200)")

    # 5. Google Social Login
    print("\n[TEST 6] Google Social Login (auto registration & sign-in)...")
    google_payload = {
        "provider": "google",
        "email": f"google.{unique_id}@apex.edu",
        "full_name": "Google Engineer",
        "access_token": "mock_google_token_12345",
    }
    g_res = client.post("/api/v1/auth/google", json=google_payload)
    assert g_res.status_code == 200
    g_data = g_res.json()
    assert g_data["user"]["email"] == f"google.{unique_id}@apex.edu"
    print(f"[OK] Google Sign-in successful: {g_data['user']['email']}")

    # 6. GitHub Social Login
    print("\n[TEST 7] GitHub Social Login (auto registration & sign-in)...")
    github_payload = {
        "provider": "github",
        "email": f"github.{unique_id}@apex.edu",
        "full_name": "GitHub Developer",
        "access_token": "mock_github_token_67890",
    }
    gh_res = client.post("/api/v1/auth/github", json=github_payload)
    assert gh_res.status_code == 200
    gh_data = gh_res.json()
    assert gh_data["user"]["email"] == f"github.{unique_id}@apex.edu"
    print(f"[OK] GitHub Sign-in successful: {gh_data['user']['email']}")

    # 7. OAuth URL Generation
    print("\n[TEST 8] Generating OAuth authorization URLs...")
    g_url_res = client.get("/api/v1/auth/oauth/google/url")
    assert g_url_res.status_code == 200
    print(f"[OK] Google Auth URL: {g_url_res.json()['auth_url']}")

    gh_url_res = client.get("/api/v1/auth/oauth/github/url")
    assert gh_url_res.status_code == 200
    print(f"[OK] GitHub Auth URL: {gh_url_res.json()['auth_url']}")

    # 8. OAuth Code Callback Exchange
    print("\n[TEST 9] OAuth callback authorization code exchange...")
    cb_res = client.post(
        "/api/v1/auth/oauth/callback",
        json={"provider": "github", "code": "mock_callback_code_456"},
    )
    assert cb_res.status_code == 200
    cb_data = cb_res.json()
    assert "access_token" in cb_data
    print(f"[OK] OAuth code exchange successful: {cb_data['user']['email']}")

    # 9. Query Authenticated /me
    print("\n[TEST 10] Testing protected /me endpoint...")
    me_token = g_data["access_token"]
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {me_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == f"google.{unique_id}@apex.edu"
    print(f"[OK] /me returned authenticated profile: {me_res.json()['full_name']}")

    print("\n" + "=" * 60)
    print("ALL AUTHENTICATION & RECOVERY TESTS PASSED SUCCESSFULLY! (10/10)")
    print("=" * 60)


if __name__ == "__main__":
    run_auth_tests()
