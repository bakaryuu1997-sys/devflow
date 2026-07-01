import pytest

from app import auth_mode
from app.auth_mode import security_checklist, validate_startup_security


def test_local_mode_allows_default_secret(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "development")
    monkeypatch.setattr(auth_mode.settings, "auth_mode", "local")
    monkeypatch.setattr(auth_mode.settings, "jwt_secret_key", "change-me")

    checks = security_checklist()

    assert any(item["key"] == "jwt_secret_strong" and not item["passed"] and not item["blocking"] for item in checks)


def test_production_mode_blocks_weak_secret(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "production")
    monkeypatch.setattr(auth_mode.settings, "jwt_secret_key", "change-me")
    monkeypatch.setattr(auth_mode.settings, "allow_public_register", False)
    monkeypatch.setattr(auth_mode.settings, "access_token_minutes", 60)

    with pytest.raises(RuntimeError):
        validate_startup_security()


def test_production_mode_passes_with_safe_config(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "production")
    monkeypatch.setattr(auth_mode.settings, "jwt_secret_key", "strong-local-test-secret-32-chars")
    monkeypatch.setattr(auth_mode.settings, "allow_public_register", False)
    monkeypatch.setattr(auth_mode.settings, "access_token_minutes", 60)
    monkeypatch.setattr(auth_mode.settings, "allow_demo_reset", False)
    monkeypatch.setattr(auth_mode.settings, "auto_create_tables", False)

    validate_startup_security()
