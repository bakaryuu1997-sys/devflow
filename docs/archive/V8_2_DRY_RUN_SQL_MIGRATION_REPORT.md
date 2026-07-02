# v8.2 — Dry-run SQL Migration Generator + Backup Checklist

## Summary

v8.2 adds a safer bridge from migration checking to actual database upgrade work. The app can now generate additive SQL statements in dry-run mode and provide a backup checklist before the user changes a local SQLite database.

## Added

- `GET /api/release-governance/dry-run-sql-migration`
- `GET /api/release-governance/backup-checklist`
- `scripts/dry_run_migration_sql.py`
- `static/migration_sql_ui.js`

## Safety choices

- SQL is generated only; it is not executed.
- Generated statements are additive: `CREATE TABLE`, `CREATE INDEX`, and `ALTER TABLE ADD COLUMN`.
- Backup and rollback steps are shown before any manual migration work.
- Existing migration checker and upgrade safety report remain unchanged.
