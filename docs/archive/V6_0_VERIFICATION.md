# v6.0 Verification

## Commands run

```bash
python scripts/quality_check.py
python -m compileall app
PYTHONPATH=. pytest -q
python scripts/security_check.py
python smoke_test_v6_0.py
```

## Results

```text
quality_check: PASS
compileall: PASS
pytest: 39 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Smoke test coverage

The smoke test verified:

- demo reset
- login
- create Requirement
- create WorkItem linked to Requirement
- filter WorkItems by Requirement
- traceability row updates with linked test count

## Warning explanation

`security_check.py` reports local-mode JWT-secret warning behavior. This matches the existing local development acceptance pattern and does not block this phase.
