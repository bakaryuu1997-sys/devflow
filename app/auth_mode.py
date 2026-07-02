from app.config import settings

LOCAL_AUTH_MODE = "local"
PRODUCTION_AUTH_MODE = "production"
WEAK_SECRETS = {"", "change-me", "changeme", "default", "test-secret"}
MIN_SECRET_LENGTH = 32


def current_auth_mode() -> str:
    if settings.environment.lower() == "production":
        return PRODUCTION_AUTH_MODE
    return settings.auth_mode.lower()


def is_production_mode() -> bool:
    return current_auth_mode() == PRODUCTION_AUTH_MODE


def local_auth_disabled() -> bool:
    """True when login is bypassed for local personal use.

    Only honoured outside production so the security posture there is unaffected.
    """
    return settings.local_no_auth and not is_production_mode()


def security_checklist() -> list[dict]:
    production = is_production_mode()
    checks = [
        _check(
            "auth_mode_set",
            "Auth mode is explicit.",
            current_auth_mode() in {LOCAL_AUTH_MODE, PRODUCTION_AUTH_MODE},
            True,
        ),
        _check(
            "jwt_secret_strong",
            "JWT secret is not a weak default and has at least 32 characters.",
            _secret_is_strong(settings.jwt_secret_key),
            production,
        ),
        _check(
            "public_register_safe",
            "Public registration is disabled in production.",
            not (production and settings.allow_public_register),
            production,
        ),
        _check(
            "token_ttl_safe",
            "Production token TTL is not excessive.",
            not (production and settings.access_token_minutes > 1440),
            production,
        ),
        _check(
            "demo_reset_disabled",
            "Demo reset is disabled in production.",
            not (production and settings.allow_demo_reset),
            production,
        ),
        _check(
            "auto_create_tables_disabled",
            "Automatic table creation is disabled in production.",
            not (production and settings.auto_create_tables),
            production,
        ),
    ]
    return checks


def validate_startup_security() -> None:
    if not settings.require_secure_production or not is_production_mode():
        return
    failed = [item for item in security_checklist() if not item["passed"] and item["blocking"]]
    if failed:
        messages = "; ".join(item["message"] for item in failed)
        raise RuntimeError(f"Production security check failed: {messages}")


def _secret_is_strong(secret: str) -> bool:
    return secret not in WEAK_SECRETS and len(secret) >= MIN_SECRET_LENGTH


def _check(key: str, message: str, passed: bool, blocking: bool) -> dict:
    return {"key": key, "message": message, "passed": passed, "blocking": blocking and not passed}
