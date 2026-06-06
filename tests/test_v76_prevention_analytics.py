from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_project(headers):
    return client.post("/api/projects", json={"name": "Prevention Analytics", "description": "v7.6"}, headers=headers).json()


def _learning_item(headers, project_id, title, status="Open", owner="", due_date=""):
    return client.post(f"/api/projects/{project_id}/release-learning-items", json={
        "title": title,
        "prevention_action": "Prevent recurring risk before release review.",
        "source": "manual",
        "status": status,
        "owner": owner,
        "due_date": due_date,
    }, headers=headers).json()["item"]


def test_v76_prevention_burndown_analytics_projection_and_markdown():
    headers = auth_headers()
    project = _create_project(headers)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    soon = (date.today() + timedelta(days=3)).isoformat()
    later = (date.today() + timedelta(days=20)).isoformat()

    _learning_item(headers, project["id"], "Done prevention", status="Prevented", owner="QA", due_date=later)
    _learning_item(headers, project["id"], "Overdue prevention", owner="QA", due_date=yesterday)
    _learning_item(headers, project["id"], "Due soon prevention", owner="PM", due_date=soon)
    _learning_item(headers, project["id"], "Missing due prevention", owner="Dev")

    data = client.get(f"/api/projects/{project['id']}/prevention-burndown-analytics", headers=headers).json()
    assert data["total_items"] == 4
    assert data["open_items"] == 3
    assert data["done_items"] == 1
    assert data["completion_rate"] == 25
    assert data["overdue_items"] == 1
    assert data["due_soon_items"] == 1
    assert data["burndown_projection"][-1]["missing_due_date_items"] == 1
    assert data["burndown_projection"][-1]["remaining_open_items"] == 1
    assert "Prevention Burndown Analytics" in data["content"]


def test_v76_owner_workload_balance_flags_unassigned_and_overloaded():
    headers = auth_headers()
    project = _create_project(headers)
    yesterday = (date.today() - timedelta(days=2)).isoformat()
    soon = (date.today() + timedelta(days=2)).isoformat()

    for index in range(3):
        _learning_item(headers, project["id"], f"QA overdue {index}", owner="QA", due_date=yesterday)
    _learning_item(headers, project["id"], "PM due soon", owner="PM", due_date=soon)
    _learning_item(headers, project["id"], "Needs owner")
    _learning_item(headers, project["id"], "Closed dev item", status="Done", owner="Dev", due_date=soon)

    data = client.get(f"/api/projects/{project['id']}/owner-workload-balance", headers=headers).json()
    qa = next(row for row in data["owners"] if row["owner"] == "QA")
    unassigned = next(row for row in data["owners"] if row["owner"] == "Unassigned")
    assert qa["status"] == "Overloaded"
    assert qa["overdue_items"] == 3
    assert data["overloaded_owner_count"] >= 1
    assert unassigned["status"] == "Needs Owner"
    assert data["unassigned_open_items"] == 1
    assert "Owner Workload Balance" in data["content"]


def test_v76_static_ui_and_routes_are_registered():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/prevention_execution_ui.js", encoding="utf-8").read() + open("static/prevention_analytics_ui.js", encoding="utf-8").read()
    routes_py = open("app/routes.py", encoding="utf-8").read()

    assert "Prevention Burndown" in index_html
    assert "Owner Workload Balance" in index_html
    assert "prevention-burndown-analytics" in ui_js
    assert "owner-workload-balance" in ui_js
    assert "routes_v76" in routes_py
