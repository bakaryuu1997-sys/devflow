from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_requirement_risk_drilldown_shows_missing_task_and_test_placeholders():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-DRILL",
            "title": "Critical billing flow",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()

    response = client.get(f"/api/requirements/{req['id']}/risk-drilldown", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["requirement_key"] == "REQ-DRILL"
    assert data["risk_count"] == 2
    assert {item["kind"] for item in data["missing_placeholders"]} == {"task", "test"}
    assert any("implementation task" in action for action in data["next_actions"])
    assert any("test WorkItem" in action for action in data["next_actions"])


def test_one_click_placeholder_creation_is_idempotent_and_reduces_risk():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-PLACEHOLDER",
            "title": "Critical payout flow",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()

    task = client.post(f"/api/requirements/{req['id']}/work-item-placeholders", json={"kind": "task"}, headers=headers)
    test = client.post(f"/api/requirements/{req['id']}/work-item-placeholders", json={"kind": "test"}, headers=headers)
    duplicate_task = client.post(
        f"/api/requirements/{req['id']}/work-item-placeholders", json={"kind": "task"}, headers=headers
    )

    assert task.status_code == 200
    assert test.status_code == 200
    assert duplicate_task.status_code == 200
    assert task.json()["id"] == duplicate_task.json()["id"]
    assert task.json()["requirement_id"] == req["id"]
    assert test.json()["kind"] == "test"

    drilldown = client.get(f"/api/requirements/{req['id']}/risk-drilldown", headers=headers).json()
    assert drilldown["missing_placeholders"] == []
    assert drilldown["risk_count"] == 0


def test_placeholder_creation_rejects_archived_requirement_and_invalid_kind():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-ARCH-PLACEHOLDER",
            "title": "Archived placeholder flow",
            "priority": "High",
            "status": "Open",
        },
        headers=headers,
    ).json()

    invalid = client.post(
        f"/api/requirements/{req['id']}/work-item-placeholders", json={"kind": "bug"}, headers=headers
    )
    client.post(f"/api/requirements/{req['id']}/archive", headers=headers)
    archived = client.post(
        f"/api/requirements/{req['id']}/work-item-placeholders", json={"kind": "task"}, headers=headers
    )

    assert invalid.status_code == 400
    assert archived.status_code == 400


def test_v64_static_ui_contains_drilldown_and_placeholder_actions():
    flow_js = open("static/flow.js", encoding="utf-8").read()
    drilldown_js = open("static/risk_drilldown_ui.js", encoding="utf-8").read()
    renderer_js = open("static/result_renderers.js", encoding="utf-8").read()
    requirement_js = open("static/requirement_ui.js", encoding="utf-8").read()

    assert "loadReleaseRiskDashboard" in flow_js
    assert "loadRequirementRiskDrilldown" in drilldown_js
    assert "work-item-placeholders" in drilldown_js
    assert "renderRequirementRiskDrilldown" in renderer_js
    assert "Create task placeholder" in renderer_js
    assert "Risk drilldown" in requirement_js
