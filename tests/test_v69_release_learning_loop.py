from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_release_learning_loop_generates_prevention_items_from_retrospective_and_risks():
    headers = auth_headers()
    project = client.post(
        "/api/projects", json={"name": "Learning Loop Project", "description": "v6.9"}, headers=headers
    ).json()
    req1 = client.post(
        f"/api/projects/{project['id']}/requirements",
        json={
            "key": "REQ-LEARN-1",
            "title": "High risk checkout",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()
    req2 = client.post(
        f"/api/projects/{project['id']}/requirements",
        json={
            "key": "REQ-LEARN-2",
            "title": "High risk billing",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()
    client.post(
        f"/api/projects/{project['id']}/work-items",
        json={
            "requirement_id": req1["id"],
            "kind": "task",
            "title": "Build checkout",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )
    client.post(
        f"/api/projects/{project['id']}/work-items",
        json={
            "requirement_id": req2["id"],
            "kind": "task",
            "title": "Build billing",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )
    client.post(
        f"/api/projects/{project['id']}/release-retrospectives",
        json={
            "author": "PM",
            "what_went_well": "Risk dashboard was useful.",
            "what_to_improve": "Start test planning before sign-off week.",
            "action_items": "Add test owner during requirement intake.\nReview recurring blocking bugs weekly.",
        },
        headers=headers,
    )

    learning = client.get(f"/api/projects/{project['id']}/release-learning-loop", headers=headers).json()
    assert learning["retrospective_count"] == 1
    assert learning["recurring_risk_signals"]
    assert any(item["source"].startswith("retrospective") for item in learning["generated_prevention_items"])
    assert "Release Learning Loop" in learning["content"]
    assert "Add test owner" in learning["content"]


def test_save_and_update_release_learning_item_status():
    headers = auth_headers()
    project = client.post(
        "/api/projects", json={"name": "Saved Learning Project", "description": "v6.9"}, headers=headers
    ).json()
    created = client.post(
        f"/api/projects/{project['id']}/release-learning-items",
        json={
            "title": "Create pre-release bug review",
            "prevention_action": "Review High/Critical bugs before release review starts.",
            "source": "manual",
            "status": "Open",
        },
        headers=headers,
    ).json()
    assert created["created"] is True
    item_id = created["item"]["id"]

    updated = client.patch(
        f"/api/release-learning-items/{item_id}", json={"status": "Prevented"}, headers=headers
    ).json()
    assert updated["item"]["status"] == "Prevented"

    learning = client.get(f"/api/projects/{project['id']}/release-learning-loop", headers=headers).json()
    assert learning["saved_item_count"] == 1
    assert "Create pre-release bug review" in learning["content"]


def test_v69_static_ui_contains_learning_loop_buttons_and_script():
    index_html = open("static/index.html", encoding="utf-8").read()
    learning_js = open("static/release_learning_ui.js", encoding="utf-8").read()

    assert "Learning Loop" in index_html
    assert "Prevention Checklist" in index_html
    assert "release_learning_ui.js" in index_html
    assert "release-learning-loop" in learning_js
    assert "release-learning-items" in learning_js
    assert "Recurring risk prevention checklist" in learning_js
