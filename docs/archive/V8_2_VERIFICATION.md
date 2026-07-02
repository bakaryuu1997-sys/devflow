# v8.2 Verification

Expected checks:

- `python scripts/quality_check.py`
- `python -m compileall app scripts tests`
- `pytest`
- `python scripts/security_check.py`
- HTTP smoke against the new v8.2 endpoints
- `python scripts/migration_check.py devflow.db`
- `python scripts/dry_run_migration_sql.py devflow.db`
