from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_create_project_from_api():
    headers = auth_headers()

    response = client.post("/api/projects", json={
        "name": "Mobile Banking",
        "description": "Risk control for mobile banking release",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Mobile Banking"


def test_create_release_for_project_from_api():
    headers = auth_headers()
    project = client.post("/api/projects", json={
        "name": "CRM Platform",
        "description": "CRM delivery project",
    }, headers=headers).json()

    response = client.post(f"/api/projects/{project['id']}/releases", json={
        "version": "1.2.0",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["version"] == "1.2.0"


def test_release_list_contains_created_release():
    headers = auth_headers()
    project = client.post("/api/projects", json={
        "name": "Payments",
        "description": "Payment release project",
    }, headers=headers).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "2.0.0"}, headers=headers)

    releases = client.get(f"/api/projects/{project['id']}/releases", headers=headers).json()

    assert any(release["version"] == "2.0.0" for release in releases)
