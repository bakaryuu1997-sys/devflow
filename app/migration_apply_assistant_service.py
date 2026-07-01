from __future__ import annotations

from sqlalchemy.orm import Session

from app.migration_checker_service import local_database_migration_check, upgrade_safety_report
from app.migration_sql_service import backup_checklist, dry_run_sql_migration


def manual_migration_apply_assistant(db: Session) -> dict:
    sql_plan = dry_run_sql_migration(db)
    backup = backup_checklist(db)
    check = local_database_migration_check(db)
    statements = sql_plan["statements"]
    data = {
        "version": "8.3",
        "mode": "manual-apply-assistant",
        "status": _assistant_status(statements, check),
        "will_apply_changes": False,
        "statement_count": len(statements),
        "backup_required": True,
        "preflight_checks": _preflight_checks(check, backup),
        "manual_apply_steps": _manual_apply_steps(statements),
        "sql_script": _sql_script(statements),
        "post_apply_verification": _post_apply_steps(),
        "dry_run": sql_plan,
    }
    data["content"] = _assistant_markdown(data)
    return data


def post_migration_verification_snapshot(db: Session) -> dict:
    check = local_database_migration_check(db)
    safety = upgrade_safety_report(db)
    dry_run = dry_run_sql_migration(db)
    remaining = dry_run["statement_count"]
    data = {
        "version": "8.3",
        "mode": "post-migration-verification",
        "status": "Verified" if check["status"] == "Ready" and remaining == 0 else "Follow-up Needed",
        "schema_ready": check["status"] == "Ready",
        "remaining_sql_count": remaining,
        "safe_to_upgrade": safety["safe_to_upgrade"],
        "verified_schema": _verified_schema(check),
        "remaining_actions": _remaining_actions(check, dry_run),
        "recommended_next_steps": _recommended_next_steps(check, remaining),
        "migration_check": check,
        "upgrade_safety": safety,
    }
    data["content"] = _verification_markdown(data)
    return data


def _assistant_status(statements: list[dict], check: dict) -> str:
    if not statements and check["status"] == "Ready":
        return "Already Migrated"
    if check["missing_tables"]:
        return "Manual Apply Required"
    return "Ready For Manual Apply"


def _preflight_checks(check: dict, backup: dict) -> list[dict]:
    return [
        {"name": "Schema check", "status": check["status"]},
        {"name": "Backup checklist", "status": backup["status"]},
        {"name": "Dry-run SQL reviewed", "status": "Required before apply"},
        {"name": "App stopped", "status": "Required before apply"},
    ]


def _manual_apply_steps(statements: list[dict]) -> list[str]:
    if not statements:
        return [
            "No SQL needs to be applied on the copied database or live database.",
            "Run post-migration verification snapshot.",
        ]
    return [
        "Stop the app and any terminals using devflow.db.",
        "Copy devflow.db to a timestamped backup file.",
        "Save the generated SQL to migrations/v8_3_manual_migration.sql.",
        "Apply SQL to a copied database first.",
        "Apply the same SQL to the real database only after the copied DB passes verification.",
        "Run scripts/post_migration_verify.py devflow.db.",
    ]


def _sql_script(statements: list[dict]) -> str:
    if not statements:
        return "-- No SQL needed for current schema.\n"
    lines = ["-- v8.3 manual migration SQL", "-- Review before applying.", "BEGIN TRANSACTION;"]
    lines.extend(row["sql"].rstrip() for row in statements)
    lines.append("COMMIT;")
    return "\n".join(lines).strip() + "\n"


def _post_apply_steps() -> list[str]:
    return [
        "python scripts/post_migration_verify.py devflow.db",
        "python scripts/migration_check.py devflow.db",
        "python -m compileall app",
        "pytest",
        "Open Governance Readiness and Upgrade Safety in the UI.",
    ]


def _verified_schema(check: dict) -> list[dict]:
    rows = []
    for row in check["required_schema"]:
        rows.append({"table": row["table"], "state": row["state"], "missing_columns": row["missing_columns"]})
    return rows


def _remaining_actions(check: dict, dry_run: dict) -> list[str]:
    actions = []
    actions.extend(f"Create missing table: {table}" for table in check["missing_tables"])
    for row in check["required_schema"]:
        actions.extend(f"Add {row['table']}.{column}" for column in row["missing_columns"])
    if dry_run["statement_count"] and not actions:
        actions.append("Review remaining dry-run SQL statements.")
    return actions or ["No remaining schema actions found."]


def _recommended_next_steps(check: dict, remaining: int) -> list[str]:
    if check["status"] == "Ready" and remaining == 0:
        return ["Keep the backup until smoke tests pass.", "Run the app and export Governance Readiness."]
    return ["Apply remaining additive SQL on a copied DB first.", "Run post_migration_verify.py again."]


def _assistant_markdown(data: dict) -> str:
    lines = [
        "# v8.3 Manual Migration Apply Assistant",
        "",
        f"Status: {data['status']}",
        f"Will apply changes: {data['will_apply_changes']}",
        "",
        "## Manual apply steps",
    ]
    lines.extend(f"- [ ] {step}" for step in data["manual_apply_steps"])
    lines.extend(["", "## SQL script", "```sql", data["sql_script"].strip(), "```", "", "## Verify after apply"])
    lines.extend(f"- [ ] {step}" for step in data["post_apply_verification"])
    return "\n".join(lines).strip() + "\n"


def _verification_markdown(data: dict) -> str:
    lines = [
        "# v8.3 Post-migration Verification Snapshot",
        "",
        f"Status: {data['status']}",
        f"Schema ready: {data['schema_ready']}",
        f"Remaining SQL count: {data['remaining_sql_count']}",
        "",
        "## Verified schema",
    ]
    lines.extend(
        f"- {row['table']}: {row['state']} missing={', '.join(row['missing_columns']) or 'none'}"
        for row in data["verified_schema"]
    )
    lines.extend(["", "## Remaining actions"])
    lines.extend(f"- {action}" for action in data["remaining_actions"])
    return "\n".join(lines).strip() + "\n"
