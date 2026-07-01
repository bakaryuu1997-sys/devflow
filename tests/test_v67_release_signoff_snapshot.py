from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_clean_release_project(headers):
    project = client.post(
        "/api/projects", json={"name": "Clean Signoff Project", "description": "v6.7"}, headers=headers
    ).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "2.0.0"}, headers=headers)
    req = client.post(
        f"/api/projects/{project['id']}/requirements",
        json={
            "key": "REQ-SIGNOFF",
            "title": "Profile settings page",
            "priority": "Medium",
            "status": "Open",
        },
        headers=headers,
    ).json()
    client.post(
        f"/api/projects/{project['id']}/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "task",
            "title": "Build profile settings page",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )
    client.post(f"/api/requirements/{req['id']}/review-complete", headers=headers)
    return project, req


def test_signoff_snapshot_blocks_unfinished_demo_release():
    headers = auth_headers()
    snapshot = client.get("/api/projects/1/release-signoff-snapshot", headers=headers).json()
    assert snapshot["ready_for_signoff"] is False
    assert snapshot["decision"] == "WAIT"
    assert snapshot["signoff_blockers"]

    rejected = client.post(
        "/api/projects/1/release-signoffs",
        json={
            "approved_by": "QA Lead",
            "approval_note": "Trying too early",
        },
        headers=headers,
    ).json()
    assert rejected["created"] is False
    assert "cannot be signed off" in rejected["message"]


def test_create_final_signoff_and_export_approval_record():
    headers = auth_headers()
    project, req = _create_clean_release_project(headers)

    snapshot = client.get(f"/api/projects/{project['id']}/release-signoff-snapshot", headers=headers).json()
    assert snapshot["ready_for_signoff"] is True
    assert snapshot["completion"]["release_review_complete"] is True
    assert snapshot["risk_dashboard"]["blocking_risks"] == 0

    created = client.post(
        f"/api/projects/{project['id']}/release-signoffs",
        json={
            "approved_by": "Release Manager",
            "approval_note": "Approved for production release.",
        },
        headers=headers,
    ).json()
    assert created["created"] is True
    assert created["signoff"]["release_version"] == "2.0.0"
    assert "Final Release Sign-off Approval Record" in created["approval_record"]
    assert "REQ-SIGNOFF" in created["approval_record"]

    records = client.get(f"/api/projects/{project['id']}/release-signoffs", headers=headers).json()
    assert len(records) == 1

    exported = client.get(f"/api/release-signoffs/{records[0]['id']}/approval-record", headers=headers).json()
    assert exported["approved_by"] == "Release Manager"
    assert "Approved for production release." in exported["content"]
    assert req["key"] in exported["content"]


def test_v67_static_ui_contains_signoff_buttons_and_script():
    index_html = open("static/index.html", encoding="utf-8").read()
    signoff_js = open("static/release_signoff_ui.js", encoding="utf-8").read()

    assert "Final Sign-off Snapshot" in index_html
    assert "Approval Records" in index_html
    assert "release_signoff_ui.js" in index_html
    assert "release-signoff-snapshot" in signoff_js
    assert "release-signoffs" in signoff_js
    assert "approval-record" in signoff_js
