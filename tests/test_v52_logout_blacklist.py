from fastapi.testclient import TestClient

from app.auth_audit_service import reset_login_limiter
from app.main import app
from app.token_blacklist_service import reset_token_blacklist

client = TestClient(app)


def setup_function():
    reset_login_limiter()
    reset_token_blacklist()


def reset_demo():
    client.post("/api/demo/reset")


def login_token():
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return response.json()["access_token"]


def test_logout_blacklists_current_token():
    reset_demo()
    token = login_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_new_login_after_logout_gets_valid_token():
    reset_demo()
    old_token = login_token()
    old_headers = {"Authorization": f"Bearer {old_token}"}
    client.post("/api/auth/logout", headers=old_headers)

    new_token = login_token()
    new_headers = {"Authorization": f"Bearer {new_token}"}

    assert client.get("/api/auth/me", headers=new_headers).status_code == 200
