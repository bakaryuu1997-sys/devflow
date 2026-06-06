# v4.3 Stable Repair Report

## What was fixed slowly and carefully

The v4.2 package had several packaging and integration issues:

1. `requirements.txt` was missing.
2. A nested old project directory was included accidentally.
3. `app/routes.py` was broken and called `router.include_router(...)` before defining `router`.
4. `app/models.py` was missing imports and base model definitions.
5. `app/schemas.py` was missing imports and core schemas.
6. `routes_core.py`, `routes_os.py`, and `routes_guards.py` were missing or empty.
7. Tests had an accidental payload key rename from `password` to `password123`.

## What is now verified

- Dependencies install successfully.
- `compileall` passes.
- Full pytest passes.
- HTTP smoke test passes for the main UI and key APIs.

## HTTP smoke tested

```text
GET  /api/health
GET  /
GET  /docs
POST /api/demo/reset
POST /api/auth/login
GET  /api/projects/1/traceability
GET  /api/projects/1/impact/REQ-001
POST /api/projects/1/git-import
POST /api/projects/1/requirement-diff
POST /api/projects/1/openapi-deep-diff
GET  /api/projects/1/workload
GET  /api/projects/1/advanced-readiness
```

## Current known non-app warning

The execution environment prints an unrelated artifact_tool spreadsheet warmup warning.
It does not block the app, tests, or HTTP smoke checks.
