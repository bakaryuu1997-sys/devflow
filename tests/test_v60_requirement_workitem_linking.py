from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_create_work_item_linked_to_requirement_updates_traceability():
    headers = auth_headers()
    req = client.post("/api/projects/1/requirements", json={
        "key": "REQ-LINK-001",
        "title": "Link work items from UI",
        "priority": "High",
        "status": "Open",
    }, headers=headers).json()

    created = client.post("/api/projects/1/work-items", json={
        "kind": "test",
        "title": "Verify requirement selector",
        "status": "Open",
        "severity": "Medium",
        "requirement_id": req["id"],
    }, headers=headers)

    assert created.status_code == 200
    assert created.json()["requirement_id"] == req["id"]

    rows = client.get("/api/projects/1/traceability", headers=headers).json()
    row = next(item for item in rows if item["requirement_key"] == "REQ-LINK-001")
    assert row["test_count"] == 1
    assert "High/Critical requirement has no test case." not in row["warnings"]


def test_filter_work_items_by_requirement_id():
    headers = auth_headers()
    req_a = client.post("/api/projects/1/requirements", json={
        "key": "REQ-FILTER-A",
        "title": "Filter A",
        "priority": "Medium",
        "status": "Open",
    }, headers=headers).json()
    req_b = client.post("/api/projects/1/requirements", json={
        "key": "REQ-FILTER-B",
        "title": "Filter B",
        "priority": "Medium",
        "status": "Open",
    }, headers=headers).json()

    client.post("/api/projects/1/work-items", json={
        "kind": "task",
        "title": "Only A task",
        "requirement_id": req_a["id"],
    }, headers=headers)
    client.post("/api/projects/1/work-items", json={
        "kind": "bug",
        "title": "Only B bug",
        "requirement_id": req_b["id"],
    }, headers=headers)

    items = client.get(f"/api/projects/1/work-items?requirement_id={req_a['id']}", headers=headers).json()

    assert any(item["title"] == "Only A task" for item in items)
    assert all(item["requirement_id"] == req_a["id"] for item in items)


def test_reject_work_item_link_to_other_project_requirement():
    headers = auth_headers()
    project = client.post("/api/projects", json={"name": "Other Project", "description": ""}, headers=headers).json()
    req = client.post(f"/api/projects/{project['id']}/requirements", json={
        "key": "REQ-OTHER-001",
        "title": "Other project requirement",
        "priority": "Low",
        "status": "Open",
    }, headers=headers).json()

    response = client.post("/api/projects/1/work-items", json={
        "kind": "task",
        "title": "Bad cross-project link",
        "requirement_id": req["id"],
    }, headers=headers)

    assert response.status_code == 400
