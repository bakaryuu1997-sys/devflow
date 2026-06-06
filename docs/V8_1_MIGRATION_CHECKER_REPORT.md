# v8.1 Migration Checker Report

## Scope
v8.1 adds a guided local database migration checker and upgrade safety report for users upgrading older SQLite databases.

## Added
- API: `GET /api/release-governance/local-migration-check`
- API: `GET /api/release-governance/upgrade-safety-report`
- CLI helper: `python scripts/migration_check.py devflow.db`
- UI buttons: `Migration Check` and `Upgrade Safety`

## Checks
The checker verifies the additive v7.x/v8.x governance schema:
- `release_signoffs.snapshot_json`
- `release_learning_items.owner`
- `release_learning_items.due_date`
- `scope_decision_audits` table and core columns

## Decision
No dependency was added. The checker uses SQLAlchemy inspector in-app and Python `sqlite3` for the CLI helper.
