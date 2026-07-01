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
    return client.post(
        "/api/projects", json={"name": "Calendar Planning", "description": "v7.7"}, headers=headers
    ).json()


def _learning_item(headers, project_id, title, status="Open", owner="", due_date=""):
    payload = {
        "title": title,
        "prevention_action": "Prevent recurring release risk before sign-off.",
        "source": "manual",
        "status": status,
        "owner": owner,
        "due_date": due_date,
    }
    return client.post(f"/api/projects/{project_id}/release-learning-items", json=payload, headers=headers).json()[
        "item"
    ]


def test_v77_prevention_calendar_groups_due_dates_and_exports_markdown():
    headers = auth_headers()
    project = _project(headers)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    soon = (date.today() + timedelta(days=5)).isoformat()

    _learning_item(headers, project["id"], "Overdue calendar item", owner="QA", due_date=yesterday)
    _learning_item(headers, project["id"], "Due soon calendar item", owner="PM", due_date=soon)
    _learning_item(headers, project["id"], "Unscheduled calendar item", owner="Dev")
    _learning_item(headers, project["id"], "Closed calendar item", status="Prevented", owner="Dev", due_date=soon)

    data = client.get(f"/api/projects/{project['id']}/prevention-calendar-view", headers=headers).json()
    assert data["open_items"] == 3
    assert data["scheduled_items"] == 2
    assert data["unscheduled_items"] == 1
    assert data["overdue_items"] == 1
    assert len(data["calendar"]) == 2
    assert data["calendar"][0]["bucket"] == "Overdue"
    assert "Prevention Calendar View" in data["content"]


def test_v77_release_readiness_timeline_scores_checkpoints():
    headers = auth_headers()
    project = _project(headers)
    yesterday = (date.today() - timedelta(days=2)).isoformat()
    soon = (date.today() + timedelta(days=7)).isoformat()
    later = (date.today() + timedelta(days=40)).isoformat()

    _learning_item(headers, project["id"], "Overdue timeline item", owner="QA", due_date=yesterday)
    _learning_item(headers, project["id"], "Soon timeline item", owner="PM", due_date=soon)
    _learning_item(headers, project["id"], "Later timeline item", owner="Dev", due_date=later)
    _learning_item(headers, project["id"], "Unscheduled timeline item")

    data = client.get(f"/api/projects/{project['id']}/release-readiness-timeline", headers=headers).json()
    assert data["open_items"] == 4
    assert data["overall_status"] == "At Risk"
    assert len(data["checkpoints"]) == 4
    assert data["checkpoints"][0]["status"] == "At Risk"
    assert data["checkpoints"][-1]["remaining_open_items"] >= 2
    assert "Release Readiness Timeline" in data["content"]


def test_v77_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/prevention_calendar_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Prevention Calendar" in index_html
    assert "Readiness Timeline" in index_html
    assert "prevention-calendar-view" in ui_js
    assert "release-readiness-timeline" in ui_js
    assert "routes_v77" in routes_py
