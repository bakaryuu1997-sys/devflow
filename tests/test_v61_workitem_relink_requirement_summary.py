from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_patch_work_item_relinks_requirement_and_traceability_counts_move():
    headers = auth_headers()
    req_a = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-REL-A",
            "title": "Original requirement",
            "priority": "High",
            "status": "Open",
        },
        headers=headers,
    ).json()
    req_b = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-REL-B",
            "title": "New requirement",
            "priority": "High",
            "status": "Open",
        },
        headers=headers,
    ).json()
    item = client.post(
        "/api/projects/1/work-items",
        json={
            "kind": "test",
            "title": "Relinkable test",
            "status": "Open",
            "severity": "Medium",
            "requirement_id": req_a["id"],
        },
        headers=headers,
    ).json()

    updated = client.patch(f"/api/work-items/{item['id']}", json={"requirement_id": req_b["id"]}, headers=headers)

    assert updated.status_code == 200
    assert updated.json()["requirement_id"] == req_b["id"]

    rows = client.get("/api/projects/1/traceability", headers=headers).json()
    row_a = next(row for row in rows if row["requirement_key"] == "REQ-REL-A")
    row_b = next(row for row in rows if row["requirement_key"] == "REQ-REL-B")
    assert row_a["test_count"] == 0
    assert row_b["test_count"] == 1


def test_patch_work_item_can_unlink_requirement():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-UNLINK",
            "title": "Can be unlinked",
            "priority": "Medium",
            "status": "Open",
        },
        headers=headers,
    ).json()
    item = client.post(
        "/api/projects/1/work-items",
        json={
            "kind": "task",
            "title": "Temporary task",
            "requirement_id": req["id"],
        },
        headers=headers,
    ).json()

    updated = client.patch(f"/api/work-items/{item['id']}", json={"requirement_id": None}, headers=headers)

    assert updated.status_code == 200
    assert updated.json()["requirement_id"] is None


def test_v61_static_ui_contains_relink_and_requirement_summary_controls():
    workitem_js = open("static/workitem_ui.js", encoding="utf-8").read()
    requirement_js = open("static/requirement_ui.js", encoding="utf-8").read()

    assert "updateWorkItemRequirement" in workitem_js
    assert "saveWorkItemTitle" in workitem_js
    assert "requirement_id: requirementId ? Number(requirementId) : null" in workitem_js
    assert "summarizeRequirementWorkItems" in requirement_js
    assert "View linked work items" in requirement_js
    assert "task" in requirement_js and "test" in requirement_js and "bug" in requirement_js
