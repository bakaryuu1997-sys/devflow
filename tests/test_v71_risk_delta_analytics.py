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
    project = client.post("/api/projects", json={"name": "Risk Delta Project", "description": "v7.1"}, headers=headers).json()
    client.post(f"/api/projects/{project['id']}/releases", json={"version": "7.1.0"}, headers=headers)
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


def _patch_snapshot(signoff_id, *, risk_count, blocking_risks, added_second=False):
    db = SessionLocal()
    try:
        signoff = db.get(ReleaseSignOff, signoff_id)
        snapshot = json.loads(signoff.snapshot_json)
        snapshot["summary"]["total_risks"] = risk_count
        snapshot["summary"]["blocking_risks"] = blocking_risks
        snapshot["requirements"][0]["risk_count"] = risk_count
        snapshot["requirements"][0]["blocking_risks"] = blocking_risks
        if added_second:
            snapshot["requirements"].append({
                "id": 999,
                "key": "REQ-DELTA-B",
                "title": "New risky scope",
                "is_done": True,
                "review_complete": True,
                "blocking_risks": 0,
                "risk_count": 1,
            })
            snapshot["summary"]["total_requirements"] = 2
            snapshot["summary"]["done_requirements"] = 2
        signoff.snapshot_json = json.dumps(snapshot)
        db.commit()
    finally:
        db.close()


def test_v71_risk_delta_between_latest_structured_snapshots():
    headers = auth_headers()
    project = _create_project(headers)
    _add_reviewed_requirement(headers, project["id"], "REQ-DELTA-A", "Delta scope")

    first = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "QA",
        "approval_note": "Base approval.",
    }, headers=headers).json()["signoff"]
    second = client.post(f"/api/projects/{project['id']}/release-signoffs", json={
        "approved_by": "QA",
        "approval_note": "Target approval.",
    }, headers=headers).json()["signoff"]
    _patch_snapshot(first["id"], risk_count=1, blocking_risks=0)
    _patch_snapshot(second["id"], risk_count=3, blocking_risks=1, added_second=True)

    delta = client.get(f"/api/projects/{project['id']}/release-risk-delta", headers=headers).json()
    assert delta["can_compare"] is True
    assert delta["summary"]["total_risks_delta"] == 2
    assert delta["summary"]["blocking_risks_delta"] == 1
    assert delta["worsened_requirements"][0]["requirement_key"] == "REQ-DELTA-A"
    assert delta["added_requirements"][0]["requirement_key"] == "REQ-DELTA-B"
    assert "Release Risk Delta Analytics" in delta["content"]
    assert delta["action_hints"]


def test_v71_risk_delta_requires_two_signoffs():
    headers = auth_headers()
    project = _create_project(headers)
    data = client.get(f"/api/projects/{project['id']}/release-risk-delta", headers=headers).json()
    assert data["can_compare"] is False
    assert "At least two" in data["message"]


def test_v71_static_ui_contains_risk_delta_controls():
    index_html = open("static/index.html", encoding="utf-8").read()
    analytics_js = open("static/release_snapshot_analytics_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Risk Delta" in index_html
    assert "release-risk-delta" in analytics_js
    assert "loadReleaseRiskDeltaAnalytics" in analytics_js
    assert "routes_v71" in routes_py
