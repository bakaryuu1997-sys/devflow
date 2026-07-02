# v7.0 Verification

```text
quality_check: PASS
compileall: PASS
pytest: 71 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Manual smoke coverage

- `/api/health` returns `200`.
- Structured snapshot is created when a final sign-off is recorded.
- Approval record export still returns Markdown content.
- Structured snapshot endpoint returns JSON snapshot data.
- Approval compare still detects added requirements.
- Snapshot analytics returns project-level snapshot counts and trend rows.

## Known warning

`security_check` reports the existing local JWT/auth warning. This is not introduced by v7.0.
