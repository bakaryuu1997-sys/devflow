# v10.8 Guarded Manual Restore Execution

v10.8 turns the v10.7 restore rehearsal into a guarded manual restore path.
It is still profile-scoped and intentionally requires a second approval phrase.

## Second approval phrase

For profile `core-risk`, the restore phrase is:

```text
RESTORE DEMO PROFILE: core-risk
```

This phrase is separate from the reset phrase used by v10.5/v10.6.
A reset phrase cannot execute restore.

## Flow

1. Export or provide a v10.6 rollback snapshot.
2. Run the v10.7 rehearsal validation.
3. Review the v10.8 guarded restore plan.
4. Type the exact restore approval phrase.
5. Delete only the selected guided sample profile rows.
6. Reinsert rows from the validated snapshot.
7. Write a restore audit event to `ActivityLog`.

## API

- `GET /api/release-governance/v10-8-guarded-restore-plan`
- `POST /api/release-governance/v10-8-guarded-restore-plan`
- `POST /api/release-governance/v10-8-execute-guarded-manual-restore`
- `GET /api/release-governance/v10-8-restore-audit-trail`
- `GET /api/release-governance/v10-8-operator-restore-execution-package`

## CLI

```bash
python scripts/export_v10_8_restore_execution_package.py v10_8_restore.md core-risk
```

## Safety notes

- The restore remains demo-profile scoped.
- Rehearsal must be ready before execution.
- Wrong profile, wrong snapshot, or wrong phrase blocks restore.
- Production restore needs a separate production approval gate.
