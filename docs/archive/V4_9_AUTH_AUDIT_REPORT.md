# v4.9 Login Rate Limit & Auth Audit Log

## Goal

Harden auth behavior without adding business features or changing the UI.

## Added

- `app/auth_audit_service.py`
- `tests/test_v49_auth_audit.py`
- audit events using existing `ActivityLog`
- in-memory failed-login throttling
- `POST /api/auth/logout`
- `GET /api/auth/audit`

## Rate limit behavior

The app tracks failed login attempts in memory.

Current rule:

```text
5 failed attempts in 5 minutes
```

After that, login returns:

```text
429 Too many failed login attempts
```

Successful login clears failed attempts for that email.

## Audit behavior

Auth events are written to `ActivityLog` with `project_id=None`.

Logged events:

```text
auth.login.success
auth.login.failed
auth.logout
```

## Endpoint

```text
GET /api/auth/audit
```

Requires manage-user permission.

## Scope control

- No UI redesign.
- No new dependency.
- No database model added.
- Existing `ActivityLog` reused to avoid pushing `models.py` beyond 200 lines.
