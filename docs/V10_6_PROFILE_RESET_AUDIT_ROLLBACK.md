# v10.6 — Profile Reset Audit Trail + Rollback Snapshot Export

v10.6 hardens the v10.5 profile reset flow by adding two operator safety layers:

1. A rollback snapshot export before reset execution.
2. An audit trail entry for every approved profile reset.

## What changed

- Added a project-scoped rollback snapshot for the selected demo profile.
- Added reset execution through a v10.6 wrapper that preserves the v10.5 approval phrase.
- Added an audit trail using `ActivityLog` instead of a new table to avoid migration risk.
- Added an operator package that combines snapshot and audit trail content.

## Safety rules

- The approval phrase remains `RESET DEMO PROFILE: <profile_id>`.
- Wrong approval still blocks execution.
- The snapshot is exported before the project-scoped delete/rebuild step.
- The legacy `/api/demo/reset` route remains unchanged.

## API

- `GET /api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk`
- `POST /api/release-governance/v10-6-execute-profile-reset?profile_id=core-risk&approval=RESET%20DEMO%20PROFILE%3A%20core-risk`
- `GET /api/release-governance/v10-6-profile-reset-audit-trail?profile_id=core-risk`
- `GET /api/release-governance/v10-6-operator-rollback-package?profile_id=core-risk`

## CLI

```bash
python scripts/export_v10_6_rollback_snapshot.py v10_6_rollback.md core-risk
```
