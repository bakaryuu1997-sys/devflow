# v9.3 Verification

Required checks:

```bash
python scripts/quality_check.py
python -m compileall app scripts
pytest
python scripts/security_check.py
python scripts/export_signature_adapter_contract_tests.py SIGNATURE_ADAPTER_CONTRACT_TESTS.md
python scripts/export_sample_signature_fixtures.py SAMPLE_SIGNATURE_FIXTURES.md
```

Expected result: all checks pass and fixtures report no private-key markers.
