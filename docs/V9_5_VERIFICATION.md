# v9.5 Verification

Expected checks:

- `python scripts/quality_check.py`
- `python -m compileall app scripts tests`
- `python -m pytest tests/test_v95_public_verifier_evidence_gate.py`
- grouped pytest for full suite when needed
- `python scripts/security_check.py`
- HTTP smoke via FastAPI TestClient
- CLI exports:
  - `export_public_verifier_evidence_package.py`
  - `export_verified_signature_approval_gate.py`

## Actual result

```text
quality_check: PASS
compileall: PASS
pytest grouped: 163 passed
security_check: PASS with local warning
HTTP smoke: PASS
export_public_verifier_evidence_package CLI: PASS
export_verified_signature_approval_gate CLI: PASS
file-size rule: PASS
```
