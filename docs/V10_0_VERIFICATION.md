# v10.0 Verification Plan

Run:

```bash
python scripts/quality_check.py
python -m compileall app scripts tests
pytest
python scripts/security_check.py
python scripts/export_final_signed_evidence_bundle.py FINAL_SIGNED_EVIDENCE_BUNDLE.md
python scripts/export_governance_rehearsal.py GOVERNANCE_REHEARSAL.md
python scripts/export_v10_governance_package.py V10_GOVERNANCE_PACKAGE.md
```
