# v5.2 Logout Token Blacklist & Browser Demo Checklist

## Goal

Address one real security weakness without opening a large feature scope.

## Fixed

Before v5.2:

```text
POST /api/auth/logout recorded an audit event but did not invalidate the token.
```

After v5.2:

```text
POST /api/auth/logout blacklists the current token.
The same token can no longer call protected endpoints.
```

## Important bug found during implementation

The first blacklist implementation failed tests because immediate re-login produced the same token.

Root cause:

```text
Token payload only had sub and exp.
Two logins in the same second could produce identical tokens.
```

Fix:

```text
Added jti random token id to the access token payload.
```

## Added

```text
app/token_blacklist_service.py
tests/test_v52_logout_blacklist.py
docs/BROWSER_VISUAL_CHECKLIST.md
```

## Behavior verified

```text
Login -> /api/auth/me returns 200
Logout -> token is blacklisted
Old token -> /api/auth/me returns 401
New login -> new token is unique
New token -> /api/auth/me returns 200
Audit log still records logout
```

## Scope control

- No UI redesign.
- No new dependency.
- No database model added.
- Token blacklist is in-memory.
