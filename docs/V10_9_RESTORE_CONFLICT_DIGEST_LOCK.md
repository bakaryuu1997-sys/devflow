# v10.9 Restore Conflict Detection + Snapshot Digest Lock

v10.9 hardens the v10.8 guarded manual restore path with two extra safety checks:
conflict detection and an explicit snapshot digest lock.

## What changed

- The restore path now compares the provided rollback snapshot against the current profile rows.
- The report lists table count deltas, missing current project state, profile mismatch, and row digest differences.
- Restore execution requires the exact snapshot digest lock in addition to the v10.8 restore phrase.
- A successful locked restore writes a dedicated digest lock audit event.

## Required operator inputs

For profile `core-risk`, a restore must provide both:

```text
RESTORE DEMO PROFILE: core-risk
```

and the exact `snapshot_digest` from the v10.6 rollback snapshot export.

## API

- `GET /api/release-governance/v10-9-restore-conflict-report`
- `POST /api/release-governance/v10-9-restore-conflict-report`
- `POST /api/release-governance/v10-9-guarded-restore-plan`
- `POST /api/release-governance/v10-9-execute-guarded-manual-restore`
- `GET /api/release-governance/v10-9-restore-digest-lock-audit-trail`
- `GET /api/release-governance/v10-9-operator-restore-conflict-package`

## CLI

```bash
python scripts/export_v10_9_restore_conflict_package.py v10_9_restore.md core-risk
```

## Safety notes

- v10.9 does not remove the v10.8 second approval phrase.
- A wrong or missing digest lock blocks execution before data is touched.
- Conflict detection is informational until the digest lock is provided.
- Production restore still needs a separate production approval gate.
