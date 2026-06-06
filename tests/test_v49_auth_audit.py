from fastapi.testclient import TestClient

from app.auth_audit_service import reset_login_limiter
from app.main import app

client = TestClient(app)


def setup_function():
    reset_login_limiter()


def reset_demo():
    client.post("/api/demo/reset")


def login(password="password123"):
    return client.post("/api/auth/login", json={"email": "admin@example.com", "password": password})


def auth_headers():
    response = login()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_failed_login_is_audited():
    reset_demo()

    response = login("wrong-password")
    logs = client.get("/api/auth/audit", headers=auth_headers()).json()

    assert response.status_code == 401
    assert any(item["action"] == "auth.login.failed" for item in logs)


def test_failed_login_rate_limit():
    reset_demo()

    for _ in range(5):
        assert login("wrong-password").status_code == 401
    response = login("wrong-password")

    assert response.status_code == 429


def test_successful_login_resets_failed_counter():
    reset_demo()

    for _ in range(4):
        assert login("wrong-password").status_code == 401
    assert login().status_code == 200
    assert login("wrong-password").status_code == 401


def test_logout_is_audited():
    reset_demo()
    headers = auth_headers()

    response = client.post("/api/auth/logout", headers=headers)
    fresh_headers = auth_headers()
    logs = client.get("/api/auth/audit", headers=fresh_headers).json()

    assert response.status_code == 200
    assert any(item["action"] == "auth.logout" for item in logs)
