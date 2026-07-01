from fastapi.testclient import TestClient

from app import auth_mode
from app.main import app

client = TestClient(app)


def _login_headers():
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _set_safe_production(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "production")
    monkeypatch.setattr(auth_mode.settings, "auth_mode", "production")
    monkeypatch.setattr(auth_mode.settings, "jwt_secret_key", "strong-local-test-secret-32-chars")
    monkeypatch.setattr(auth_mode.settings, "allow_public_register", False)
    monkeypatch.setattr(auth_mode.settings, "access_token_minutes", 60)
    monkeypatch.setattr(auth_mode.settings, "auto_create_tables", False)
    monkeypatch.setattr(auth_mode.settings, "allow_demo_reset", False)


def test_production_write_api_requires_authentication(monkeypatch):
    _set_safe_production(monkeypatch)

    response = client.post("/api/demo/fix")

    assert response.status_code == 401


def test_production_demo_reset_is_blocked_even_for_admin(monkeypatch):
    client.post("/api/demo/reset")
    _set_safe_production(monkeypatch)
    headers = _login_headers()

    response = client.post("/api/demo/reset", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Demo reset is disabled"


def test_public_register_cannot_self_assign_admin_role(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "development")
    monkeypatch.setattr(auth_mode.settings, "auth_mode", "local")
    monkeypatch.setattr(auth_mode.settings, "allow_public_register", True)
    client.post("/api/demo/reset")

    response = client.post(
        "/api/auth/register",
        json={"email": "role-escalation@example.com", "password": "password123", "role": "admin"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "viewer"


def _sample_path(path: str) -> str:
    replacements = {
        "project_id": "1",
        "release_id": "1",
        "requirement_id": "1",
        "item_id": "1",
        "signoff_id": "1",
        "note_id": "1",
        "step_id": "sample-step",
    }
    for key, value in replacements.items():
        path = path.replace("{" + key + "}", value)
    return path


def test_all_production_unsafe_routes_require_authentication(monkeypatch):
    _set_safe_production(monkeypatch)
    public_paths = {"/api/auth/login", "/api/auth/register"}
    unsafe_methods = {"POST", "PUT", "PATCH", "DELETE"}

    checked = []
    for route in app.routes:
        methods = getattr(route, "methods", set()) or set()
        path = getattr(route, "path", "")
        for method in sorted(methods & unsafe_methods):
            if path in public_paths:
                continue
            response = client.request(method, _sample_path(path), json={})
            assert response.status_code == 401, f"{method} {path} returned {response.status_code}"
            checked.append((method, path))

    assert checked


def test_local_write_auth_required_blocks_unsafe_routes(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "development")
    monkeypatch.setattr(auth_mode.settings, "auth_mode", "local")
    monkeypatch.setattr(auth_mode.settings, "local_write_auth_required", True)

    response = client.post("/api/demo/fix")

    assert response.status_code == 401

