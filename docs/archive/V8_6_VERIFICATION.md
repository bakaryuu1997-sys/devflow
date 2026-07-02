# v8.6 Verification

Expected checks:

```bash
python scripts/quality_check.py
python -m compileall app scripts
pytest
python scripts/security_check.py
python scripts/migration_check.py devflow.db
python scripts/dry_run_migration_sql.py devflow.db
python scripts/manual_migration_apply_assistant.py devflow.db
python scripts/post_migration_verify.py devflow.db
python scripts/safe_copy_migration_apply.py devflow.db devflow.copy.db
python scripts/rollback_drill.py devflow.db
python scripts/production_upgrade_checklist.py devflow.db
python scripts/real_migration_gate.py devflow.db
python scripts/export_upgrade_runbook.py devflow.db /tmp/RUNBOOK.md
python scripts/operator_handoff_package.py devflow.db /tmp/operator_handoff_v8_6
```

v8.6 should pass without adding dependencies or mutating the production database through the new scripts.
