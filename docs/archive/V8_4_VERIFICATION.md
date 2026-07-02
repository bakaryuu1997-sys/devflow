# v8.4 Verification

```text
quality_check: PASS
compileall: PASS
pytest: 114 passed
security_check: PASS with local warning
HTTP smoke: PASS
migration_check CLI: PASS
dry_run_migration_sql CLI: PASS
manual_migration_apply_assistant CLI: PASS
post_migration_verify CLI: PASS
safe_copy_migration_apply CLI: PASS
rollback_drill CLI: PASS
file-size rule: PASS
```

The local security warning is the existing development auth/JWT warning and is not introduced by v8.4.
