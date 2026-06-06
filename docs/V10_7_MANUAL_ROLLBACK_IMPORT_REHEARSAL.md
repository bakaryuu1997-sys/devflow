# v10.7 Manual rollback import rehearsal + restore checklist

v10.7 adds a safe restore rehearsal layer after v10.6 rollback snapshots.
It validates a rollback snapshot and gives an operator checklist, but it does
not automatically write rollback rows back into the database.

## Scope

- Rehearse manual rollback import from a v10.6 snapshot.
- Validate profile id, snapshot readiness, required rows, and table counts.
- Export a restore checklist and operator package.
- Keep the v10.5 approval phrase and v10.6 audit trail unchanged.

## API

- `GET /api/release-governance/v10-7-manual-rollback-import-rehearsal`
- `POST /api/release-governance/v10-7-manual-rollback-import-rehearsal`
- `GET /api/release-governance/v10-7-restore-checklist`
- `GET /api/release-governance/v10-7-operator-restore-package`

## Operator rule

v10.7 is intentionally a dry run. If the rehearsal reports a profile or digest
mismatch, the operator should stop and export a fresh v10.6 rollback package.

## CLI

```bash
python scripts/export_v10_7_restore_rehearsal.py v10_7_restore_rehearsal.md core-risk
```

## Next step

After this rehearsal passes repeatedly, the next safe increment can add guarded
manual restore execution with a second explicit approval phrase.
