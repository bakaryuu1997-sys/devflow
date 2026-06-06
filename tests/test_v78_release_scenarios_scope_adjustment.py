from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _project(headers):
    return client.post("/api/projects", json={"name": "Scenario Planning", "description": "v7.8"}, headers=headers).json()


def _learning_item(headers, project_id, title, status="Open", owner="", due_date=""):
    payload = {
        "title": title,
        "prevention_action": "Prevent recurring release risk before sign-off.",
        "source": "manual",
        "status": status,
        "owner": owner,
        "due_date": due_date,
    }
    return client.post(f"/api/projects/{project_id}/release-learning-items", json=payload, headers=headers).json()["item"]


def test_v78_release_readiness_scenarios_compare_scope_choices():
    headers = auth_headers()
    project = _project(headers)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    soon = (date.today() + timedelta(days=5)).isoformat()

    _learning_item(headers, project["id"], "Overdue scope item", owner="QA", due_date=yesterday)
    _learning_item(headers, project["id"], "Soon scope item", owner="Dev", due_date=soon)
    _learning_item(headers, project["id"], "Unscheduled scope item", owner="PM")
    _learning_item(headers, project["id"], "Already prevented item", status="Prevented")

    data = client.get(f"/api/projects/{project['id']}/release-readiness-scenarios?target_days=7", headers=headers).json()
    names = [row["name"] for row in data["scenarios"]]

    assert data["active_scope_items"] == 3
    assert data["target_days"] == 7
    assert "Baseline" in names
    assert "Complete overdue first" in names
    assert "Defer unscheduled" in names
    assert data["scenarios"][0]["status"] == "At Risk"
    assert max(row["readiness_score"] for row in data["scenarios"]) > data["scenarios"][0]["readiness_score"]
    assert "Release Readiness Scenario Planning" in data["content"]


def test_v78_scope_adjustment_can_defer_item_from_active_scope():
    headers = auth_headers()
    project = _project(headers)
    item = _learning_item(headers, project["id"], "Defer me", owner="QA")

    result = client.post(
        f"/api/release-learning-items/{item['id']}/scope-adjustment",
        json={"status": "Deferred", "reason": "Not required for this release."},
        headers=headers,
    ).json()

    assert result["updated"] is True
    assert result["item"]["status"] == "Deferred"
    assert "Scope note" in result["item"]["prevention_action"]
    assert "Prevention Scope Adjustment" in result["content"]

    scenarios = client.get(f"/api/projects/{project['id']}/release-readiness-scenarios", headers=headers).json()
    assert scenarios["active_scope_items"] == 0
    assert scenarios["scoped_out_items"] == 1


def test_v78_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/prevention_scenario_ui.js", encoding="utf-8").read()
    routes_py = open("app/routes.py", encoding="utf-8").read()

    assert "Scenario Planning" in index_html
    assert "release-readiness-scenarios" in ui_js
    assert "scope-adjustment" in ui_js
    assert "routes_v78" in routes_py
