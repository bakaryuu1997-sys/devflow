from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_project(headers):
    return client.post("/api/projects", json={"name": "Prevention Execution", "description": "v7.5"}, headers=headers).json()


def _learning_item(headers, project_id, title, status="Open", owner="", due_date=""):
    return client.post(f"/api/projects/{project_id}/release-learning-items", json={
        "title": title,
        "prevention_action": "Control recurring release risk before it reaches sign-off.",
        "source": "manual",
        "status": status,
        "owner": owner,
        "due_date": due_date,
    }, headers=headers).json()["item"]


def test_v75_prevention_execution_board_lanes_and_markdown():
    headers = auth_headers()
    project = _create_project(headers)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    soon = (date.today() + timedelta(days=3)).isoformat()
    future = (date.today() + timedelta(days=30)).isoformat()

    _learning_item(headers, project["id"], "Unplanned prevention")
    _learning_item(headers, project["id"], "Planned prevention", owner="QA", due_date=future)
    _learning_item(headers, project["id"], "Due soon prevention", owner="PM", due_date=soon)
    overdue = _learning_item(headers, project["id"], "Overdue prevention", owner="Release owner", due_date=yesterday)
    _learning_item(headers, project["id"], "Closed prevention", status="Prevented", owner="QA", due_date=future)

    board = client.get(f"/api/projects/{project['id']}/prevention-execution-board", headers=headers).json()
    assert board["open_items"] == 4
    assert board["planned_items"] == 3
    assert board["unplanned_items"] == 1
    assert board["due_soon_items"] == 1
    assert board["overdue_items"] == 1
    assert board["done_items"] == 1
    assert len(board["lanes"]["Overdue"]) == 1
    assert len(board["lanes"]["Due Soon"]) == 1
    assert len(board["lanes"]["Planned"]) == 1
    assert len(board["lanes"]["Unplanned"]) == 1
    assert "Prevention Execution Board" in board["content"]
    assert overdue["id"] == board["lanes"]["Overdue"][0]["id"]


def test_v75_escalate_item_and_overdue_risk_escalations():
    headers = auth_headers()
    project = _create_project(headers)
    yesterday = (date.today() - timedelta(days=8)).isoformat()
    item = _learning_item(headers, project["id"], "Escalate recurring blocker", owner="QA", due_date=yesterday)

    escalated = client.post(f"/api/release-learning-items/{item['id']}/escalate", json={
        "reason": "Missed due date before next release readiness review."
    }, headers=headers).json()
    assert escalated["changed"] is True
    assert escalated["item"]["status"] == "Escalated"
    assert "Escalation note" in escalated["item"]["prevention_action"]

    board = client.get(f"/api/projects/{project['id']}/prevention-execution-board", headers=headers).json()
    assert board["escalated_items"] == 1
    assert board["lanes"]["Escalated"][0]["id"] == item["id"]

    escalations = client.get(f"/api/projects/{project['id']}/overdue-risk-escalations", headers=headers).json()
    assert escalations["overdue_items"] == 1
    assert escalations["escalated_items"] == 1
    assert escalations["escalations"][0]["level"] in {"High", "Critical"}
    assert "Overdue Risk Escalations" in escalations["content"]


def test_v75_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    learning_js = open("static/release_learning_ui.js", encoding="utf-8").read() + open("static/prevention_execution_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())

    assert "Prevention Execution Board" in index_html
    assert "Overdue Escalations" in index_html
    assert "prevention-execution-board" in learning_js
    assert "overdue-risk-escalations" in learning_js
    assert "escalateReleaseLearningItem" in learning_js
    assert "routes_v75" in routes_py
