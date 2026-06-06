# v9.4 Verification

Expected checks:

```bash
python scripts/quality_check.py
python -m compileall app scripts
python -m pytest tests/test_v94_public_key_verifier.py -q
python scripts/security_check.py
python scripts/export_public_key_verifier_readiness.py PUBLIC_KEY_VERIFIER_READINESS.md
python scripts/public_key_verifier_dry_run.py PUBLIC_KEY_VERIFIER_DRY_RUN.md
```

The verifier dry-run should return `Verified` when the optional `cryptography` package is available.
