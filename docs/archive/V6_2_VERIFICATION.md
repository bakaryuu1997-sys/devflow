# v6.2 Verification

## Commands run

```bash
python scripts/quality_check.py
python -m compileall app static scripts tests
pytest -q
python scripts/security_check.py
PYTHONPATH=. python /tmp/smoke_v62.py
```

## Result

```text
quality_check: PASS
compileall: PASS
pytest: 45 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Smoke flow verified

- Reset demo data.
- Login as demo admin.
- Create a Critical Requirement.
- Edit Requirement title and priority.
- Create a linked WorkItem.
- Run risk scan and confirm Requirement-specific risk is visible.
- Archive the Requirement.
- Run risk scan again and confirm archived Requirement is ignored.
- Load the main UI page.

## Security note

`security_check.py` still reports local auth mode and the existing JWT-secret warning behavior. This matches the accepted local development pattern and is not a v6.2 regression.
