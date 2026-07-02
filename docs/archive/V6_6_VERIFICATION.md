# v6.6 Verification

```text
quality_check: PASS
compileall: PASS
pytest: 59 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Manual smoke coverage

- Demo reset works.
- Login works.
- Release review completion endpoint returns requirement rows.
- Requirement done gates endpoint returns per-gate pass/fail state.
- Requirement review cannot be completed until gates pass.
- Review can be reopened.
- Existing v6.5 checklist export still works.
