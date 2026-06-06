# v8.7 Production Upgrade Rehearsal + Operator Sign-off Report

## Scope

v8.7 adds a production upgrade rehearsal report and operator sign-off checklist on top of the v8.6 handoff package.

## Added

- API: `GET /api/release-governance/production-upgrade-rehearsal-report`
- API: `GET /api/release-governance/operator-signoff-checklist`
- CLI: `python scripts/export_rehearsal_report.py devflow.db REHEARSAL_REPORT.md`
- CLI: `python scripts/operator_signoff_checklist.py devflow.db OPERATOR_SIGNOFF_CHECKLIST.md`
- UI buttons: `Rehearsal Report`, `Operator Sign-off`

## Safety

- Does not apply migration to the production database.
- Keeps the v8.5 approval phrase gate unchanged.
- Focuses on rehearsal evidence, operator attestations, and final sign-off readiness.
