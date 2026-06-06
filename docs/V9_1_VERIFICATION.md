# v9.1 Verification

```text
quality_check: PASS
compileall: PASS
pytest grouped: 143 passed
security_check: PASS with local warning
HTTP smoke: PASS
migration_check CLI: PASS
dry_run_migration_sql CLI: PASS
export_signed_payload_import_package CLI: PASS
export_timestamp_token_evidence_package CLI: PASS
file-size rule: PASS
```

Note: one-shot full pytest can hit the execution timeout in this environment, so tests were run in grouped batches covering all test files.
