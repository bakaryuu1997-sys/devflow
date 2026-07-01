from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _project(headers):
    return client.post("/api/projects", json={"name": "Plan Recommendation", "description": "v7.9"}, headers=headers).json()


def _learning_item(headers, project_id, title, owner="", due_date=""):
    payload = {
        "title": title,
        "prevention_action": "Prevent recurring release risk before sign-off.",
        "source": "manual",
        "status": "Open",
        "owner": owner,
        "due_date": due_date,
    }
    return client.post(f"/api/projects/{project_id}/release-learning-items", json=payload, headers=headers).json()["item"]


def test_v79_release_plan_recommendation_picks_better_scenario():
    headers = auth_headers()
    project = _project(headers)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    _learning_item(headers, project["id"], "Overdue recommendation item", owner="QA", due_date=yesterday)
    _learning_item(headers, project["id"], "Unscheduled recommendation item", owner="PM")

    data = client.get(f"/api/projects/{project['id']}/release-plan-recommendation?target_days=7", headers=headers).json()

    assert data["recommended_plan"]["name"] != "Baseline"
    assert data["expected_score_gain"] > 0
    assert data["ranked_scenarios"][0]["readiness_score"] >= data["baseline_score"]
    assert "Release Plan Recommendation" in data["content"]


def test_v79_scope_decision_audit_records_adjustments():
    headers = auth_headers()
    project = _project(headers)
    item = _learning_item(headers, project["id"], "Audit me")

    client.post(
        f"/api/release-learning-items/{item['id']}/scope-adjustment",
        json={"status": "Out of Scope", "reason": "Not part of this release plan."},
        headers=headers,
    )
    audit = client.get(f"/api/projects/{project['id']}/scope-decision-audit", headers=headers).json()

    assert audit["audit_count"] == 1
    assert audit["decisions"][0]["old_status"] == "Open"
    assert audit["decisions"][0]["new_status"] == "Out of Scope"
    assert "Not part of this release plan" in audit["decisions"][0]["reason"]
    assert "Scope Decision Audit Trail" in audit["content"]


def test_v79_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/release_plan_recommendation_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Plan Recommendation" in index_html
    assert "Scope Audit" in index_html
    assert "release-plan-recommendation" in ui_js
    assert "scope-decision-audit" in ui_js
    assert "routes_v79" in routes_py
