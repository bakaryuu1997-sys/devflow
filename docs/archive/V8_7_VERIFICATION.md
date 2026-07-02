# v8.7 Verification

## Result

```text
quality_check: PASS
compileall: PASS
pytest grouped: 127 passed
security_check: PASS with local warning
HTTP smoke: PASS
migration_check CLI: PASS
dry_run_migration_sql CLI: PASS
manual_migration_apply_assistant CLI: PASS
post_migration_verify CLI: PASS
safe_copy_migration_apply CLI: PASS
rollback_drill CLI: PASS
production_upgrade_checklist CLI: PASS
real_migration_gate CLI: PASS blocked without approval phrase
export_upgrade_runbook CLI: PASS
operator_handoff_package CLI: PASS
export_rehearsal_report CLI: PASS
operator_signoff_checklist CLI: PASS
file-size rule: PASS
```

## Note

The full one-shot pytest command can exceed the execution timeout in this environment, so tests were also run in grouped batches that covered all test files.
