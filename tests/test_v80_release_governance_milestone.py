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
    payload = {"name": "Governance Milestone", "description": "v8.0"}
    return client.post("/api/projects", json=payload, headers=headers).json()


def _learning_item(headers, project_id, due_date=""):
    payload = {
        "title": "Governance prevention item",
        "prevention_action": "Prevent recurring risk before release governance review.",
        "source": "manual",
        "status": "Open",
        "owner": "QA",
        "due_date": due_date,
    }
    return client.post(f"/api/projects/{project_id}/release-learning-items", json=payload, headers=headers).json()[
        "item"
    ]


def test_v80_governance_readiness_exposes_checks_and_migration_notes():
    headers = auth_headers()
    project = _project(headers)
    item = _learning_item(headers, project["id"], (date.today() + timedelta(days=3)).isoformat())
    client.post(
        f"/api/release-learning-items/{item['id']}/scope-adjustment",
        json={"status": "Deferred", "reason": "Move to the next release governance scope."},
        headers=headers,
    )

    data = client.get(f"/api/projects/{project['id']}/release-governance-readiness", headers=headers).json()

    assert data["project_id"] == project["id"]
    assert data["scope_audit_count"] == 1
    assert data["score"] >= 50
    assert any(row["name"] == "Structured snapshots" for row in data["checks"])
    assert any(row["area"] == "ScopeDecisionAudit" for row in data["migration_notes"])
    assert "Release Governance Readiness" in data["content"]


def test_v80_migration_notes_endpoint_is_exportable():
    data = client.get("/api/release-governance/migration-notes").json()

    assert data["version"] == "8.0"
    assert any("snapshot_json" in row["area"] for row in data["notes"])
    assert "v8.0 Migration Notes" in data["content"]


def test_v80_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/release_governance_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Governance Readiness" in index_html
    assert "Migration Notes" in index_html
    assert "release-governance-readiness" in ui_js
    assert "migration-notes" in ui_js
    assert "routes_v80" in routes_py
