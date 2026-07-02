# DevFlow Guard v5.1 Final Bug Bash & Manual Demo Validation

## Goal

Run the release candidate like a real user would, following `docs/DEMO_SCRIPT.md`, without adding new product features.

## Bug found

The v5.0 package documented these demo files:

```text
dangerous_migration.sql
app_errors.log
test_report_failed.xml
openapi_before.json
openapi_after.json
```

but they were missing from `examples/`.

## Fix applied

Added the missing example files:

```text
examples/dangerous_migration.sql
examples/app_errors.log
examples/test_report_failed.xml
examples/openapi_before.json
examples/openapi_after.json
```

No app feature was added.

## Manual demo validation

The HTTP demo flow passed 26/26 steps.

Validated:

```text
GET /api/health
GET /
GET /docs
POST /api/demo/reset
POST /api/auth/login
GET /api/projects/1/today
GET /api/projects/1/dashboard
POST /api/projects/1/guards/sql
POST /api/projects/1/guards/logs
POST /api/projects/1/guards/tests
POST /api/projects/1/guards/api-diff
GET /api/projects/1/guards
GET /api/projects/1/traceability
POST /api/projects/1/requirement-changes
GET /api/projects/1/impact/REQ-001
POST /api/projects/1/code-risk
POST /api/projects/1/env-guard
POST /api/projects/1/git-import
POST /api/projects/1/requirement-diff
POST /api/projects/1/openapi-deep-diff
GET /api/projects/1/workload
GET /api/projects/1/advanced-readiness
GET /api/projects/1/evidence?release_id=1
GET /api/projects/1/evidence.md?release_id=1
GET /api/security/checklist
GET /api/auth/audit
```

## Result

The package is now more demo-ready because the documented examples exist and the demo flow is verified.
