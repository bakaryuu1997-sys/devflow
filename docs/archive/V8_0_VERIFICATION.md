# v8.0 Verification

Expected verification commands:

```bash
python scripts/quality_check.py
python -m compileall app tests
pytest
python scripts/security_check.py
```

Smoke target:
- `/api/release-governance/migration-notes`
- `/api/projects/1/release-governance-readiness`
