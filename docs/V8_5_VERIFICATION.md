# v8.5 Verification

Expected verification set:

```bash
python scripts/quality_check.py
python -m compileall app scripts
pytest
python scripts/security_check.py
python scripts/migration_check.py devflow.db
python scripts/dry_run_migration_sql.py devflow.db
python scripts/manual_migration_apply_assistant.py devflow.db
python scripts/post_migration_verify.py devflow.db
python scripts/safe_copy_migration_apply.py devflow.db devflow.v8_5_test_copy.db
python scripts/rollback_drill.py devflow.db
python scripts/production_upgrade_checklist.py devflow.db
python scripts/real_migration_gate.py devflow.db
```

The unapproved `real_migration_gate.py` command is expected to block when migration SQL is pending. Tests cover the approved path on a temporary database.
