from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_patch_requirement_updates_title_priority_and_status():
    headers = auth_headers()
    req = client.post("/api/projects/1/requirements", json={
        "key": "REQ-EDIT",
        "title": "Old requirement title",
        "priority": "Medium",
        "status": "Open",
    }, headers=headers).json()

    response = client.patch(f"/api/requirements/{req['id']}", json={
        "title": "New requirement title",
        "priority": "Critical",
        "status": "In Progress",
    }, headers=headers)

    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New requirement title"
    assert updated["priority"] == "Critical"
    assert updated["status"] == "In Progress"


def test_archive_requirement_hides_it_from_risk_scan_and_dashboard_requirement_count():
    headers = auth_headers()
    req = client.post("/api/projects/1/requirements", json={
        "key": "REQ-ARCHIVE-RISK",
        "title": "Critical requirement with no task or test",
        "priority": "Critical",
        "status": "Open",
    }, headers=headers).json()

    before = client.post("/api/projects/1/risks/run", headers=headers).json()
    assert any(risk["requirement_id"] == req["id"] for risk in before)

    archived = client.post(f"/api/requirements/{req['id']}/archive", headers=headers)
    assert archived.status_code == 200
    assert archived.json()["status"] == "Archived"

    after = client.post("/api/projects/1/risks/run", headers=headers).json()
    assert all(risk["requirement_id"] != req["id"] for risk in after)

    dashboard = client.get("/api/projects/1/dashboard", headers=headers).json()
    all_requirements = client.get("/api/projects/1/requirements", headers=headers).json()
    archived_count = len([item for item in all_requirements if item["status"] == "Archived"])
    assert dashboard["requirements"] == len(all_requirements) - archived_count


def test_v62_static_ui_contains_requirement_edit_archive_and_risk_visibility():
    requirement_js = open("static/requirement_ui.js", encoding="utf-8").read()
    workitem_js = open("static/workitem_ui.js", encoding="utf-8").read()
    requirement_css = open("static/requirement_ui.css", encoding="utf-8").read()

    assert "saveRequirementTitle" in requirement_js
    assert "updateRequirementField" in requirement_js
    assert "archiveRequirementFromUi" in requirement_js
    assert "showRequirementRisks" in requirement_js
    assert "summarizeRequirementRisks" in requirement_js
    assert "riskSummary" in requirement_js
    assert "status !== \"Archived\"" in workitem_js
    assert "requirement-risk-pill" in requirement_css
