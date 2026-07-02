# v8.3 Manual Migration Apply Assistant Report

## Completed

- Added a manual migration apply assistant API.
- Added a post-migration verification snapshot API.
- Added terminal helpers for manual apply planning and verification.
- Added UI buttons for both workflow steps.
- Kept database changes manual and backup-first.

## API

- `GET /api/release-governance/manual-migration-apply-assistant`
- `GET /api/release-governance/post-migration-verification-snapshot`

## CLI

```bash
python scripts/manual_migration_apply_assistant.py devflow.db
python scripts/post_migration_verify.py devflow.db
```

## Safety rule

v8.3 does not auto-apply SQL to the live database. The user should copy the DB, apply SQL to the copy first, verify, then repeat manually only after the copy passes.
