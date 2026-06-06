# v8.4 Safe Migration Copy + Rollback Drill Report

## Goal

Add a safer migration workflow that applies generated SQL only to a copied SQLite database first, then verifies rollback drill behavior before any real database upgrade.

## Added

- `GET /api/release-governance/safe-copy-migration-apply`
- `GET /api/release-governance/rollback-drill-automation`
- `python scripts/safe_copy_migration_apply.py devflow.db devflow.v8_4_migration_copy.db`
- `python scripts/rollback_drill.py devflow.db`

## Safety position

The original database is never modified by the v8.4 apply helper. The script copies the database, applies additive migration SQL to that copy, then verifies the copy schema. The rollback drill creates a backup and restored copy, then checks file hashes to confirm rollback behavior.

## UI

Step 6 now includes:

- Safe Copy Apply
- Rollback Drill

## Limitations

This is still not automatic production migration. It is a local safety drill for SQLite databases. Real migration should only happen after backup, copied DB verification, rollback drill, and smoke tests pass.
