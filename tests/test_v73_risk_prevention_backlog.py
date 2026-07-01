import json

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import ReleaseSignOff
from app.routes import wired_route_modules

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_project(headers):
    project = client.post(
        "/api/projects", json={"name": "Prevention Backlog Project", "description": "v7.3"}, headers=headers
    ).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "7.3.0"}, headers=headers)
    return project


def _add_reviewed_requirement(headers, project_id):
    req = client.post(
        f"/api/projects/{project_id}/requirements",
        json={
            "key": "REQ-PREVENT",
            "title": "Prevention ready scope",
            "priority": "Medium",
            "status": "Open",
        },
        headers=headers,
    ).json()
    client.post(
        f"/api/projects/{project_id}/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "task",
            "title": "Implement prevention scope",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )
    client.post(f"/api/requirements/{req['id']}/review-complete", headers=headers)
    return req


def _inject_risk_event(signoff_id, rule_id, severity="High", blocking=True):
    db = SessionLocal()
    try:
        signoff = db.get(ReleaseSignOff, signoff_id)
        snapshot = json.loads(signoff.snapshot_json)
        snapshot["requirements"][0]["risk_count"] = 1
        snapshot["requirements"][0]["blocking_risks"] = 1 if blocking else 0
        snapshot["requirements"][0]["highest_severity"] = severity
        snapshot["requirements"][0]["risk_events"] = [
            {
                "rule_id": rule_id,
                "title": "Repeated unstable release gate",
                "message": "This risk keeps returning.",
                "severity": severity,
                "blocking": blocking,
            }
        ]
        snapshot["summary"]["total_risks"] = 1
        snapshot["summary"]["blocking_risks"] = 1 if blocking else 0
        signoff.snapshot_json = json.dumps(snapshot)
        db.commit()
    finally:
        db.close()


def _create_two_risky_signoffs(headers, project_id):
    first = client.post(
        f"/api/projects/{project_id}/release-signoffs",
        json={
            "approved_by": "QA",
            "approval_note": "First approval.",
        },
        headers=headers,
    ).json()["signoff"]
    second = client.post(
        f"/api/projects/{project_id}/release-signoffs",
        json={
            "approved_by": "QA",
            "approval_note": "Second approval.",
        },
        headers=headers,
    ).json()["signoff"]
    _inject_risk_event(first["id"], "recurring_unstable_gate")
    _inject_risk_event(second["id"], "recurring_unstable_gate")


def test_v73_risk_prevention_backlog_from_recurring_trends():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"])
    _create_two_risky_signoffs(headers, project["id"])

    data = client.get(f"/api/projects/{project['id']}/risk-prevention-backlog", headers=headers).json()
    assert data["can_analyze"] is True
    assert data["open_backlog_count"] == 1
    assert data["backlog_items"][0]["rule_id"] == "recurring_unstable_gate"
    assert data["backlog_items"][0]["priority"] == "Critical"
    assert data["backlog_items"][0]["already_saved"] is False
    assert "Risk Prevention Backlog" in data["content"]


def test_v73_auto_create_learning_items_is_idempotent():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"])
    _create_two_risky_signoffs(headers, project["id"])

    created = client.post(f"/api/projects/{project['id']}/risk-prevention-backlog/auto-create", headers=headers).json()
    assert created["created"] == 1
    assert created["backlog"]["saved_backlog_count"] == 1
    assert created["backlog"]["backlog_items"][0]["already_saved"] is True

    second = client.post(f"/api/projects/{project['id']}/risk-prevention-backlog/auto-create", headers=headers).json()
    assert second["created"] == 0
    assert second["skipped"] == 1

    learning = client.get(f"/api/projects/{project['id']}/release-learning-loop", headers=headers).json()
    assert any(
        item["source"] == "recurring-risk:recurring_unstable_gate" for item in learning["saved_prevention_items"]
    )


def test_v73_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    analytics_js = open("static/release_snapshot_analytics_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Risk Prevention Backlog" in index_html
    assert "risk-prevention-backlog" in analytics_js
    assert "autoCreateRiskPreventionItems" in analytics_js
    assert "routes_v73" in routes_py
