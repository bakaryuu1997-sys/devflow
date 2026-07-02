# v7.1 Verification

Expected verification commands:

```text
python scripts/quality_check.py
python -m compileall app tests
pytest
python scripts/security_check.py
HTTP smoke test
file-size rule
```

Observed status:

```text
quality_check: PASS
compileall: PASS
pytest: PASS
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

The local warning is the existing development security warning and is not introduced by v7.1.
