from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_convert_placeholder_into_real_work_item():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-CONVERT",
            "title": "Critical ledger export",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()
    placeholder = client.post(
        f"/api/requirements/{req['id']}/work-item-placeholders",
        json={"kind": "task"},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/work-items/{placeholder['id']}/convert-placeholder",
        json={"title": "Implement ledger export path", "status": "In Progress", "severity": "High"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == placeholder["id"]
    assert data["title"] == "Implement ledger export path"
    assert data["status"] == "In Progress"
    assert data["severity"] == "High"
    assert data["requirement_id"] == req["id"]


def test_convert_placeholder_rejects_normal_work_item():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-NORMAL",
            "title": "Normal task flow",
            "priority": "Medium",
            "status": "Open",
        },
        headers=headers,
    ).json()
    item = client.post(
        "/api/projects/1/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "task",
            "title": "Already real task",
            "status": "Open",
            "severity": "Medium",
        },
        headers=headers,
    ).json()

    response = client.post(
        f"/api/work-items/{item['id']}/convert-placeholder",
        json={"title": "Rename real task"},
        headers=headers,
    )

    assert response.status_code == 400


def test_release_review_checklist_exports_markdown_with_actions():
    headers = auth_headers()
    client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-CHECKLIST",
            "title": "Critical payment capture",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    )

    response = client.get("/api/projects/1/release-review-checklist", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["release_status"] == "Blocked"
    assert data["blocking_risks"] >= 1
    assert "# Release Review Checklist" in data["content"]
    assert "REQ-CHECKLIST" in data["content"]
    assert "- [ ]" in data["content"]
    assert "Top actions" in data["content"]


def test_v65_static_ui_contains_conversion_and_checklist_export():
    index_html = open("static/index.html", encoding="utf-8").read()
    drilldown_js = open("static/risk_drilldown_ui.js", encoding="utf-8").read()
    export_js = open("static/release_review_export_ui.js", encoding="utf-8").read()
    renderer_js = open("static/result_renderers.js", encoding="utf-8").read()

    assert "Export Release Review Checklist" in index_html
    assert "loadReleaseReviewChecklist" in export_js
    assert "release-review-checklist" in export_js
    assert "convert-placeholder" in drilldown_js
    assert "Convert placeholder" in renderer_js
