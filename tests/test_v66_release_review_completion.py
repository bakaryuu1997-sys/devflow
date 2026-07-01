from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_requirement_done_gates_block_until_task_test_and_risks_pass():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-GATE",
            "title": "Critical audit export",
            "priority": "Critical",
            "status": "Open",
        },
        headers=headers,
    ).json()

    blocked = client.get(f"/api/requirements/{req['id']}/done-gates", headers=headers).json()
    assert blocked["is_done"] is False
    assert any(gate["key"] == "done_task" and gate["passed"] is False for gate in blocked["gates"])
    assert any(gate["key"] == "done_test" and gate["passed"] is False for gate in blocked["gates"])

    client.post(
        "/api/projects/1/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "task",
            "title": "Implement audit export",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )
    client.post(
        "/api/projects/1/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "test",
            "title": "Audit export regression test",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )

    passed = client.get(f"/api/requirements/{req['id']}/done-gates", headers=headers).json()
    assert passed["is_done"] is True
    assert passed["blocking_risks"] == 0


def test_review_complete_requires_done_gates_and_tracks_project_completion():
    headers = auth_headers()
    req = client.post(
        "/api/projects/1/requirements",
        json={
            "key": "REQ-REVIEW",
            "title": "Medium profile page",
            "priority": "Medium",
            "status": "Open",
        },
        headers=headers,
    ).json()

    rejected = client.post(f"/api/requirements/{req['id']}/review-complete", headers=headers)
    assert rejected.status_code == 200
    assert rejected.json()["marked"] is False

    client.post(
        "/api/projects/1/work-items",
        json={
            "requirement_id": req["id"],
            "kind": "task",
            "title": "Build profile page",
            "status": "Done",
            "severity": "Medium",
        },
        headers=headers,
    )
    marked = client.post(f"/api/requirements/{req['id']}/review-complete", headers=headers).json()
    assert marked["marked"] is True
    assert marked["review_complete"] is True
    assert marked["is_done"] is True

    completion = client.get("/api/projects/1/release-review-completion", headers=headers).json()
    reviewed = [row for row in completion["requirements"] if row["requirement_id"] == req["id"]][0]
    assert reviewed["review_complete"] is True
    assert completion["reviewed_requirements"] >= 1

    reopened = client.post(f"/api/requirements/{req['id']}/review-reopen", headers=headers).json()
    assert reopened["review_complete"] is False


def test_v66_static_ui_contains_completion_and_done_gates():
    index_html = open("static/index.html", encoding="utf-8").read()
    completion_js = open("static/release_completion_ui.js", encoding="utf-8").read()
    renderer_js = open("static/release_completion_renderers.js", encoding="utf-8").read()
    requirement_js = open("static/requirement_ui.js", encoding="utf-8").read()

    assert "Release Review Completion" in index_html
    assert "release_completion_ui.js" in index_html
    assert "release-review-completion" in completion_js
    assert "review-complete" in completion_js
    assert "renderReleaseReviewCompletion" in renderer_js
    assert "release_completion_renderers.js" in index_html
    assert "Done gates" in requirement_js
