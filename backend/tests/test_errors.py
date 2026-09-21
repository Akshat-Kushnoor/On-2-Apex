def test_not_found_error_format(client):
    response = client.get("/non-existent-path")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]


def test_method_not_allowed_format(client):
    response = client.post("/health")
    assert response.status_code == 405
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert "message" in data["error"]
