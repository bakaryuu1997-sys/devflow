# v4.8 Auth Hardening for Local/Production Modes

## Goal

Separate local/offline auth expectations from production auth requirements.

## Added

- `app/auth_mode.py`
- `app/routes_security.py`
- `scripts/security_check.py`
- `tests/test_v48_auth_hardening.py`

## Behavior

### Local mode

Local mode allows developer-friendly defaults but reports weak secrets as warnings.

Example:

```text
Auth mode: local
WARN: jwt_secret_strong
```

This is useful for offline demo and local development.

### Production mode

Production mode blocks unsafe settings.

Blocked when:

- `JWT_SECRET_KEY=change-me`
- public registration is enabled
- token TTL is too long

## New endpoint

```text
GET /api/security/checklist
```

Returns:

```text
auth_mode
passed
checks
```

## New script

```bash
python scripts/security_check.py
```

## Startup protection

When `ENVIRONMENT=production` and `REQUIRE_SECURE_PRODUCTION=true`, unsafe production config raises startup error.

## Scope control

- No UI redesign.
- No large auth library change.
- No new dependency.
- Local/offline flow remains easy.
