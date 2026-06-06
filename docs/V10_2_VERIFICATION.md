# v10.2 Verification

Expected verification commands:

```bash
python scripts/quality_check.py
python -m compileall app scripts tests
python -m pytest tests/test_v102_first_run_wizard_reset_hardening.py
python scripts/security_check.py
python scripts/export_v10_2_first_run_wizard.py V10_2_FIRST_RUN_WIZARD.md
python scripts/export_v10_2_demo_reset_safety.py V10_2_DEMO_RESET_SAFETY.md
python scripts/export_v10_2_operator_first_run_package.py V10_2_OPERATOR_FIRST_RUN_PACKAGE.md
```

The release should keep the v8.5 production migration gate unchanged.
