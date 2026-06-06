# v6.4 Verification

```text
quality_check: PASS
compileall: PASS
pytest: 52 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Commands Used

```bash
python scripts/quality_check.py
python -m compileall app tests static
pytest -q
python scripts/security_check.py
uvicorn app.main:app --host 127.0.0.1 --port 8765
curl -fsS http://127.0.0.1:8765/api/health
```

## Smoke Coverage

- Health endpoint returned OK.
- Demo reset completed.
- Login completed.
- Release-risk dashboard returned grouped Requirement risk data.
- Requirement risk drilldown returned selected Requirement details.

## Warning

`security_check` still reports the existing local-mode JWT warning. This is not introduced by v6.4.
