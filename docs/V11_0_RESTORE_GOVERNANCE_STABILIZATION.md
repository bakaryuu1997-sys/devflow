# v11.0 — Restore governance stabilization + final operator recovery runbook

v11.0 stabilizes the reset/rollback/restore flow introduced in v10.5-v10.9. It does not add a new destructive operation. It gives the operator one final readiness report, a recovery runbook, and a package that combines the existing conflict and digest-lock evidence.

## Safety model

- Reset approval phrase stays `RESET DEMO PROFILE: <profile_id>`.
- Restore approval phrase stays `RESTORE DEMO PROFILE: <profile_id>`.
- Restore still requires the exact v10.6 snapshot digest lock.
- v11.0 does not bypass v10.7 rehearsal or v10.9 conflict detection.
- v11.0 does not add automatic restore scheduling.

## API

- `POST /api/release-governance/v11-0-restore-governance-stability-report`
- `POST /api/release-governance/v11-0-final-operator-recovery-runbook`
- `GET /api/release-governance/v11-0-operator-recovery-package`

## CLI

```bash
python scripts/export_v11_0_operator_recovery_package.py v11_0_recovery.md core-risk
```

## Operator sequence

1. Export a v10.6 rollback snapshot.
2. Run v10.7 rehearsal against that snapshot.
3. Review v10.9 conflict detection.
4. Copy the exact snapshot digest lock.
5. Execute v10.9 restore only with restore phrase, digest lock, and operator name.
6. Review restore and digest-lock audit trails.

## Boundary

This milestone is a stabilization milestone. It intentionally avoids adding a third approval phrase, broad database restore, or production migration behavior.
