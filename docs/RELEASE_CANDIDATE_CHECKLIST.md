# Release Candidate Checklist

## Required checks

Run:

```bash
python scripts/quality_check.py
python -m compileall app
pytest
python scripts/security_check.py
```

## Manual smoke flow

1. Start app.
2. Open `/`.
3. Reset demo.
4. Login.
5. Run traceability.
6. Run advanced readiness.
7. Open evidence report.
8. Open `/api/security/checklist`.
9. Trigger one failed login.
10. Confirm `/api/auth/audit` shows auth activity.

## Release candidate rules

Do not add new product features in RC.

Allowed changes:

- documentation fixes
- broken link fixes
- test fixes
- packaging fixes
- critical bug fixes

Not allowed:

- large UI rewrites
- new integrations
- new business modules
- dependency-heavy changes
