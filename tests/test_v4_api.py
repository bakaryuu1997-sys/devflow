from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def headers():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_traceability_api():
    h = headers()
    response = client.get("/api/projects/1/traceability", headers=h)

    assert response.status_code == 200
    assert response.json()


def test_requirement_change_and_impact_api():
    h = headers()
    change = client.post(
        "/api/projects/1/requirement-changes",
        json={"requirement_key": "REQ-001", "old_text": "Login by email", "new_text": "Login by email or phone"},
        headers=h,
    )
    impact = client.get("/api/projects/1/impact/REQ-001", headers=h)

    assert change.status_code == 200
    assert impact.status_code == 200
    assert "suggested_actions" in impact.json()


def test_code_risk_and_env_guard_api():
    h = headers()
    code = client.post(
        "/api/projects/1/code-risk",
        json={"source": "manual", "files": ["src/auth/login.py", "migrations/001.sql"]},
        headers=h,
    )
    env = client.post(
        "/api/projects/1/env-guard",
        json={"content": "DATABASE_URL=x\nJWT_SECRET_KEY=change-me\nAPP_DEBUG=true"},
        headers=h,
    )

    assert code.status_code == 200
    assert env.status_code == 200
    assert any(item["blocking"] for item in env.json())


def test_advanced_readiness_api():
    h = headers()
    response = client.get("/api/projects/1/advanced-readiness", headers=h)

    assert response.status_code == 200
    assert "score" in response.json()
