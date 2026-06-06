from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_create_and_update_work_item_from_api():
    headers = auth_headers()

    created = client.post("/api/projects/1/work-items", json={
        "kind": "test",
        "title": "Add login regression test",
        "status": "Open",
        "severity": "High",
        "requirement_id": None,
    }, headers=headers)

    assert created.status_code == 200
    item_id = created.json()["id"]

    updated = client.patch(f"/api/work-items/{item_id}", json={"status": "Done"}, headers=headers)

    assert updated.status_code == 200
    assert updated.json()["status"] == "Done"


def test_work_items_list_contains_created_item():
    headers = auth_headers()

    client.post("/api/projects/1/work-items", json={
        "kind": "bug",
        "title": "Fix release blocker",
        "status": "Open",
        "severity": "Critical",
        "requirement_id": None,
    }, headers=headers)
    items = client.get("/api/projects/1/work-items", headers=headers).json()

    assert any(item["title"] == "Fix release blocker" for item in items)
