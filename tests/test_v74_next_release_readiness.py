from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_project(headers):
    project = client.post("/api/projects", json={"name": "Next Release Planning", "description": "v7.4"}, headers=headers).json()
    return project


def test_v74_learning_item_accepts_owner_due_date_and_updates_planning():
    headers = auth_headers()
    project = _create_project(headers)
    created = client.post(f"/api/projects/{project['id']}/release-learning-items", json={
        "title": "Prevent recurring blocker",
        "prevention_action": "Assign a release owner before sign-off.",
        "source": "manual",
        "status": "Open",
        "owner": "QA Lead",
        "due_date": "2099-01-10",
    }, headers=headers).json()

    item = created["item"]
    assert item["owner"] == "QA Lead"
    assert item["due_date"] == "2099-01-10"

    updated = client.patch(f"/api/release-learning-items/{item['id']}/planning", json={
        "owner": "Release Manager",
        "due_date": "2099-01-15",
    }, headers=headers).json()
    assert updated["item"]["owner"] == "Release Manager"
    assert updated["item"]["due_date"] == "2099-01-15"

    learning = client.get(f"/api/projects/{project['id']}/release-learning-loop", headers=headers).json()
    saved = learning["saved_prevention_items"][0]
    assert saved["owner"] == "Release Manager"
    assert saved["due_date"] == "2099-01-15"


def test_v74_next_release_readiness_flags_unplanned_and_ready_states():
    headers = auth_headers()
    project = _create_project(headers)
    first = client.post(f"/api/projects/{project['id']}/release-learning-items", json={
        "title": "Plan test coverage",
        "prevention_action": "Add owner and deadline for test coverage.",
        "source": "manual",
        "status": "Open",
    }, headers=headers).json()["item"]
    second = client.post(f"/api/projects/{project['id']}/release-learning-items", json={
        "title": "Close recurring release risk",
        "prevention_action": "Close the recurring blocker.",
        "source": "manual",
        "status": "Open",
        "owner": "QA",
        "due_date": "2099-02-01",
    }, headers=headers).json()["item"]

    readiness = client.get(f"/api/projects/{project['id']}/next-release-readiness", headers=headers).json()
    assert readiness["open_items"] == 2
    assert readiness["unassigned_items"] == 1
    assert readiness["missing_due_date_items"] == 1
    assert readiness["status"] in {"Planning Needed", "At Risk"}
    assert "Next Release Readiness" in readiness["content"]

    client.patch(f"/api/release-learning-items/{first['id']}/planning", json={
        "owner": "PM",
        "due_date": "2099-02-02",
        "status": "Prevented",
    }, headers=headers)
    client.patch(f"/api/release-learning-items/{second['id']}", json={"status": "Prevented"}, headers=headers)
    ready = client.get(f"/api/projects/{project['id']}/next-release-readiness", headers=headers).json()
    assert ready["open_items"] == 0
    assert ready["status"] == "Ready"
    assert ready["score"] == 100


def test_v74_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    learning_js = open("static/release_learning_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Next Release Readiness" in index_html
    assert "next-release-readiness" in learning_js
    assert "updateReleaseLearningItemPlanning" in learning_js
    assert "routes_v74" in routes_py
