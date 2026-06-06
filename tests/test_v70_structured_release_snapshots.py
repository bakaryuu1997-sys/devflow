from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_project(headers):
    project = client.post("/api/projects", json={"name": "Structured Snapshot Project", "description": "v7.0"}, headers=headers).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "7.0.0"}, headers=headers)
    return project


def _add_reviewed_requirement(headers, project_id, key, title):
    req = client.post(f"/api/projects/{project_id}/requirements", json={
        "key": key,
        "title": title,
        "priority": "Medium",
        "status": "Open",
    }, headers=headers).json()
    client.post(f"/api/projects/{project_id}/work-items", json={
        "requirement_id": req["id"],
        "kind": "task",
        "title": f"Implement {title}",
        "status": "Done",
        "severity": "Medium",
    }, headers=headers)
    client.post(f"/api/requirements/{req['id']}/review-complete", headers=headers)
    return req


def test_signoff_stores_and_exports_structured_snapshot():
    headers = auth_headers()
    project = _create_project(headers)
    req = _add_reviewed_requirement(headers, project["id"], "REQ-JSON-1", "Structured approval scope")

    created = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "Release Manager",
        "approval_note": "Stored as JSON snapshot.",
    }, headers=headers).json()
    assert created["created"] is True
    assert created["signoff"]["has_structured_snapshot"] is True

    exported = client.get(f"/api/release-signoffs/{created['signoff']['id']}/approval-record", headers=headers).json()
    structured = exported["structured_snapshot"]
    assert structured["schema_version"] == "7.0"
    assert structured["release"]["version"] == "7.0.0"
    assert structured["approval"]["approved_by"] == "Release Manager"
    assert structured["requirements"][0]["key"] == req["key"]


def test_snapshot_analytics_and_structured_compare_use_json_rows():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"], "REQ-JSON-A", "First JSON scope")
    first = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "QA",
        "approval_note": "First JSON approval.",
    }, headers=headers).json()["signoff"]

    _add_reviewed_requirement(headers, project["id"], "REQ-JSON-B", "Second JSON scope")
    client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "QA",
        "approval_note": "Second JSON approval.",
    }, headers=headers)

    compare = client.get(f"/api/projects/{project['id']}/release-signoffs/compare", headers=headers).json()
    assert compare["can_compare"] is True
    assert compare["added_requirements"][0]["requirement_key"] == "REQ-JSON-B"

    analytics = client.get(f"/api/projects/{project['id']}/release-snapshot-analytics", headers=headers).json()
    assert analytics["snapshot_count"] == 2
    assert analytics["structured_snapshot_count"] == 2
    assert analytics["requirement_count_seen"] == 2

    snap = client.get(f"/api/release-signoffs/{first['id']}/structured-snapshot", headers=headers).json()
    assert snap["has_structured_snapshot"] is True
    assert snap["structured_snapshot"]["requirements"][0]["key"] == "REQ-JSON-A"


def test_v70_static_ui_contains_structured_snapshot_controls():
    index_html = open("static/index.html", encoding="utf-8").read()
    analytics_js = open("static/release_snapshot_analytics_ui.js", encoding="utf-8").read()

    assert "Snapshot Analytics" in index_html
    assert "release_snapshot_analytics_ui.js" in index_html
    assert "release-snapshot-analytics" in analytics_js
    assert "structured-snapshot" in analytics_js
    assert "Structured release snapshot analytics" in analytics_js
