from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_create_requirement_from_api():
    headers = auth_headers()

    response = client.post("/api/projects/1/requirements", json={
        "key": "REQ-EXPORT-001",
        "title": "Export evidence report",
        "priority": "High",
        "status": "Open",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["key"] == "REQ-EXPORT-001"


def test_requirement_list_contains_created_requirement():
    headers = auth_headers()
    client.post("/api/projects/1/requirements", json={
        "key": "REQ-AUDIT-001",
        "title": "Show auth audit log",
        "priority": "Medium",
        "status": "Open",
    }, headers=headers)

    requirements = client.get("/api/projects/1/requirements", headers=headers).json()

    assert any(item["key"] == "REQ-AUDIT-001" for item in requirements)


def test_traceability_includes_created_requirement():
    headers = auth_headers()
    client.post("/api/projects/1/requirements", json={
        "key": "REQ-RISK-001",
        "title": "Show release risk score",
        "priority": "Critical",
        "status": "Open",
    }, headers=headers)

    rows = client.get("/api/projects/1/traceability", headers=headers).json()

    assert any(row["requirement_key"] == "REQ-RISK-001" for row in rows)
