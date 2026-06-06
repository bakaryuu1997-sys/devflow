# v7.8 Verification

```text
quality_check: PASS
compileall: PASS
pytest: 95 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Manual smoke path

1. Login or reset demo.
2. Open Learning Loop or Risk Prevention Backlog.
3. Add prevention items with owner and due date.
4. Open Scenario Planning.
5. Compare baseline against scope-adjustment scenarios.
6. Defer or mark an item out of scope.
7. Reload Scenario Planning and confirm active scope changes.

## Notes

The security warning is the existing local JWT/auth mode warning, not a v7.8 regression.
