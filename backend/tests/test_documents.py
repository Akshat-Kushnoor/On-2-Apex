import io
import pytest
from app.services.storage import storage_service


@pytest.fixture
def auth_header_doc_user(client):
    email = "docuser@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Doc User"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf_content():
    try:
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        stream = io.BytesIO()
        writer.write(stream)
        stream.seek(0)
        return stream.getvalue()
    except Exception:
        return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


def test_upload_rejects_non_pdf(client, auth_header_doc_user):
    fake_file = io.BytesIO(b"Hello world text file")
    files = {"file": ("test.txt", fake_file, "text/plain")}
    resp = client.post("/api/v1/documents/upload", files=files, headers=auth_header_doc_user)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_upload_and_extract_pdf(client, auth_header_doc_user, sample_pdf_content):
    pdf_file = io.BytesIO(sample_pdf_content)
    files = {"file": ("resume.pdf", pdf_file, "application/pdf")}
    resp = client.post("/api/v1/documents/upload", files=files, headers=auth_header_doc_user)
    assert resp.status_code == 201
    doc_data = resp.json()
    assert doc_data["status"] == "processed"
    doc_id = doc_data["id"]

    list_resp = client.get("/api/v1/documents", headers=auth_header_doc_user)
    assert list_resp.status_code == 200
    assert any(d["id"] == doc_id for d in list_resp.json())

    extract_resp = client.get(f"/api/v1/documents/{doc_id}/extraction", headers=auth_header_doc_user)
    assert extract_resp.status_code == 200
    extract_data = extract_resp.json()
    assert extract_data["status"] == "proposed"
    assert "skills" in extract_data["extracted_data"]

    md_resp = client.get(f"/api/v1/documents/{doc_id}/markdown", headers=auth_header_doc_user)
    assert md_resp.status_code == 200
    assert "markdown" in md_resp.json()


def test_approve_document_extraction(client, auth_header_doc_user, sample_pdf_content):
    pdf_file = io.BytesIO(sample_pdf_content)
    files = {"file": ("resume2.pdf", pdf_file, "application/pdf")}
    upload_resp = client.post("/api/v1/documents/upload", files=files, headers=auth_header_doc_user)
    doc_id = upload_resp.json()["id"]

    approval_payload = {
        "approve_skills": True,
        "approve_projects": True,
        "custom_skills": [
            {"name": "FastAPI", "category": "Frameworks & Libraries", "proficiency": "Advanced"}
        ],
        "custom_projects": [
            {"title": "Docling Resume Parser", "technologies": ["Python", "FastAPI"]}
        ],
    }

    approve_resp = client.post(
        f"/api/v1/documents/{doc_id}/approve",
        json=approval_payload,
        headers=auth_header_doc_user,
    )
    assert approve_resp.status_code == 200

    profile_resp = client.get("/api/v1/profile", headers=auth_header_doc_user)
    profile_data = profile_resp.json()
    assert any(s["name"] == "FastAPI" for s in profile_data["skills"])
    assert any(p["title"] == "Docling Resume Parser" for p in profile_data["projects"])
