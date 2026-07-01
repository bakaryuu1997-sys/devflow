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
        "/api/projects", json={"name": "Recurring Risk Project", "description": "v7.2"}, headers=headers
    ).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "7.2.0"}, headers=headers)
    return project


def _add_reviewed_requirement(headers, project_id, key):
    req = client.post(
        f"/api/projects/{project_id}/requirements",
        json={
            "key": key,
            "title": "Recurring risk scope",
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
            "title": "Implement recurring scope",
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
        snapshot["schema_version"] = "7.2"
        snapshot["requirements"][0]["risk_count"] = 1
        snapshot["requirements"][0]["blocking_risks"] = 1 if blocking else 0
        snapshot["requirements"][0]["highest_severity"] = severity
        snapshot["requirements"][0]["risk_events"] = [
            {
                "rule_id": rule_id,
                "title": "Repeated missing test coverage",
                "message": "Risk appeared again in this snapshot.",
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


def test_v72_snapshot_contains_rich_risk_events_when_current_risk_exists():
    headers = auth_headers()
    project = _create_project(headers)
    req = client.post(
        f"/api/projects/{project['id']}/requirements",
        json={
            "key": "REQ-RICH-RISK",
            "title": "High priority needs test",
            "priority": "High",
            "status": "Open",
        },
        headers=headers,
    ).json()
    client.post(
        f"/api/projects/{project['id']}/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "task",
            "title": "Implement high priority scope",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )

    snapshot = client.get(f"/api/projects/{project['id']}/release-signoff-snapshot", headers=headers).json()
    row = snapshot["structured_snapshot"]["requirements"][0]
    assert snapshot["structured_snapshot"]["risk_event_schema_version"] == "7.2"
    assert row["risk_events"][0]["rule_id"] == "critical_requirement_without_test"
    assert row["highest_severity"] in {"High", "Critical"}


def test_v72_recurring_risk_trends_from_structured_snapshots():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"], "REQ-RECUR-A")
    first = client.post(
        f"/api/projects/{project['id']}/release-signoffs",
        json={
            "approved_by": "QA",
            "approval_note": "First approval.",
        },
        headers=headers,
    ).json()["signoff"]
    second = client.post(
        f"/api/projects/{project['id']}/release-signoffs",
        json={
            "approved_by": "QA",
            "approval_note": "Second approval.",
        },
        headers=headers,
    ).json()["signoff"]
    _inject_risk_event(first["id"], "repeated_missing_test")
    _inject_risk_event(second["id"], "repeated_missing_test")

    data = client.get(f"/api/projects/{project['id']}/recurring-risk-trends", headers=headers).json()
    assert data["can_analyze"] is True
    assert data["recurring_risks"][0]["rule_id"] == "repeated_missing_test"
    assert data["recurring_risks"][0]["snapshot_occurrences"] == 2
    assert "Recurring Risk Trends" in data["content"]
    assert data["action_hints"]


def test_v72_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    analytics_js = open("static/release_snapshot_analytics_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Recurring Risk Trends" in index_html
    assert "recurring-risk-trends" in analytics_js
    assert "loadRecurringRiskTrends" in analytics_js
    assert "routes_v72" in routes_py
