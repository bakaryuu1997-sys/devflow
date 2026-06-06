from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_project(headers):
    project = client.post("/api/projects", json={"name": "History Compare Project", "description": "v6.8"}, headers=headers).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "3.0.0"}, headers=headers)
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


def test_compare_release_approval_history_detects_added_requirement():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"], "REQ-HIST-1", "First approved scope")
    first = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "QA Lead",
        "approval_note": "First approval.",
    }, headers=headers).json()
    assert first["created"] is True

    _add_reviewed_requirement(headers, project["id"], "REQ-HIST-2", "Second approved scope")
    second = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "QA Lead",
        "approval_note": "Second approval with added scope.",
    }, headers=headers).json()
    assert second["created"] is True

    compare = client.get(f"/api/projects/{project['id']}/release-signoffs/compare", headers=headers).json()
    assert compare["can_compare"] is True
    assert compare["note_changed"] is True
    assert compare["added_requirements"][0]["requirement_key"] == "REQ-HIST-2"
    assert "Release Approval History Compare" in compare["summary_markdown"]


def test_create_list_and_export_post_release_retrospective_note():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"], "REQ-RETRO", "Retrospective scope")
    signoff = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "Release Manager",
        "approval_note": "Ready.",
    }, headers=headers).json()["signoff"]

    created = client.post(f"/api/projects/{project['id']}/release-retrospectives", json={
        "signoff_id": signoff["id"],
        "author": "PM",
        "what_went_well": "Release gates were visible.",
        "what_to_improve": "Start risk review earlier.",
        "action_items": "Add pre-review checkpoint.",
    }, headers=headers).json()
    assert created["created"] is True
    assert "Post-release Retrospective Note" in created["content"]

    notes = client.get(f"/api/projects/{project['id']}/release-retrospectives", headers=headers).json()
    assert len(notes) == 1
    exported = client.get(f"/api/release-retrospectives/{notes[0]['id']}/export", headers=headers).json()
    assert exported["author"] == "PM"
    assert "Add pre-review checkpoint" in exported["content"]


def test_v68_static_ui_contains_history_and_retrospective_buttons():
    index_html = open("static/index.html", encoding="utf-8").read()
    history_js = open("static/release_history_ui.js", encoding="utf-8").read()

    assert "Compare Approvals" in index_html
    assert "Retrospectives" in index_html
    assert "release_history_ui.js" in index_html
    assert "release-signoffs/compare" in history_js
    assert "release-retrospectives" in history_js
    assert "Post-release" in history_js
