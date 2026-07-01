from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_release_risk_dashboard_groups_risks_by_requirement_with_fix_hints():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-DASH",
            "title": "Critical checkout flow",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()
    client.post(
        "/api/projects/1/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "bug",
            "title": "Checkout fails",
            "status": "Open",
            "severity": "Critical",
        },
        headers=headers,
    )

    response = client.get("/api/projects/1/release-risk-dashboard", headers=headers)

    assert response.status_code == 200
    data = response.json()
    selected = next(row for row in data["requirements"] if row["requirement_key"] == "REQ-DASH")
    assert data["release_status"] == "Blocked"
    assert selected["risk_count"] == 3
    assert selected["blocking_risks"] == 2
    assert selected["highest_severity"] == "Critical"
    assert any("test WorkItem" in hint for hint in selected["fix_hints"])
    assert any("implementation task" in hint for hint in selected["fix_hints"])
    assert any("high/critical bugs" in hint for hint in selected["fix_hints"])
    assert any(action.startswith("REQ-DASH:") for action in data["top_actions"])


def test_release_risk_dashboard_excludes_archived_requirements():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-DASH-ARCHIVED",
            "title": "Archived risky requirement",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()
    client.post(f"/api/requirements/{req['id']}/archive", headers=headers)

    data = client.get("/api/projects/1/release-risk-dashboard", headers=headers).json()

    assert all(row["requirement_key"] != "REQ-DASH-ARCHIVED" for row in data["requirements"])


def test_v63_static_ui_contains_release_risk_dashboard_by_requirement():
    flow_js = open("static/flow.js", encoding="utf-8").read()
    renderer_js = open("static/result_renderers.js", encoding="utf-8").read()
    index_html = open("static/index.html", encoding="utf-8").read()

    assert "loadReleaseRiskDashboard" in flow_js
    assert "release-risk-dashboard" in flow_js
    assert "renderReleaseRiskDashboard" in renderer_js
    assert "Fix hints" in renderer_js
    assert "Risk Dashboard by Requirement" in index_html
