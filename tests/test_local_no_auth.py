"""Local no-auth mode: login can be bypassed for personal localhost use."""

from fastapi.testclient import TestClient

from app import auth_mode, seed
from app.main import app

seed.main()  # ensure a default admin exists for the bypass to resolve to
client = TestClient(app)


def test_auth_config_defaults_to_login_required():
    cfg = client.get("/api/auth/config").json()
    assert cfg["login_required"] is True
    assert cfg["no_auth"] is False


def test_no_auth_mode_reports_disabled_login(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "local_no_auth", True)
    cfg = client.get("/api/auth/config").json()
    assert cfg["no_auth"] is True
    assert cfg["login_required"] is False


def test_no_auth_mode_resolves_default_admin_without_token(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "local_no_auth", True)
    response = client.get("/api/auth/me")  # no Authorization header
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_no_auth_mode_allows_writes_without_token(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "local_no_auth", True)
    response = client.post("/api/projects", json={"name": "NoAuth", "description": "d"})
    assert response.status_code == 200


def test_no_auth_is_ignored_in_production(monkeypatch):
    # Even with the flag on, production must still require authentication.
    monkeypatch.setattr(auth_mode.settings, "local_no_auth", True)
    monkeypatch.setattr(auth_mode.settings, "environment", "production")
    monkeypatch.setattr(auth_mode.settings, "auth_mode", "production")
    assert auth_mode.local_auth_disabled() is False
    assert client.get("/api/auth/config").json()["no_auth"] is False
