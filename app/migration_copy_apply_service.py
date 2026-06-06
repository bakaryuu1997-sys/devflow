from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.migration_apply_assistant_service import post_migration_verification_snapshot
from app.migration_sql_service import backup_checklist, dry_run_sql_migration


def safe_copy_migration_apply_assistant(db: Session) -> dict:
    dry_run = dry_run_sql_migration(db)
    source_path = _sqlite_path()
    copy_path = _copy_path(source_path)
    data = {
        "version": "8.4",
        "mode": "safe-copy-migration-apply",
        "status": "Copy Apply Ready" if dry_run["statement_count"] else "No Copy Apply Needed",
        "will_modify_original_database": False,
        "will_apply_to_copied_database": bool(dry_run["statement_count"]),
        "source_database": str(source_path) if source_path else "non-sqlite-or-unknown",
        "recommended_copy_database": str(copy_path) if copy_path else "not-available",
        "statement_count": dry_run["statement_count"],
        "preflight_checks": _preflight(dry_run, source_path),
        "copy_apply_steps": _copy_apply_steps(source_path, copy_path, dry_run),
        "commands": _commands(source_path, copy_path),
        "sql_script": _sql_script(dry_run["statements"]),
        "dry_run": dry_run,
    }
    data["content"] = _copy_apply_markdown(data)
    return data


def rollback_drill_automation_plan(db: Session) -> dict:
    source_path = _sqlite_path()
    copy_path = _copy_path(source_path)
    backup = backup_checklist(db)
    verify = post_migration_verification_snapshot(db)
    data = {
        "version": "8.4",
        "mode": "rollback-drill-automation",
        "status": "Rollback Drill Ready" if source_path else "SQLite Database Required",
        "will_modify_original_database": False,
        "source_database": str(source_path) if source_path else "non-sqlite-or-unknown",
        "recommended_copy_database": str(copy_path) if copy_path else "not-available",
        "drill_steps": _rollback_steps(source_path, copy_path),
        "commands": _rollback_commands(source_path, copy_path),
        "success_criteria": _success_criteria(),
        "backup_checklist": backup,
        "post_migration_verification": verify,
    }
    data["content"] = _rollback_markdown(data)
    return data


def _sqlite_path() -> Path | None:
    url = settings.database_url
    if not url.startswith("sqlite:///"):
        return None
    raw = url.replace("sqlite:///", "", 1)
    return Path(raw).resolve()


def _copy_path(source_path: Path | None) -> Path | None:
    if source_path is None:
        return None
    return source_path.with_name(f"{source_path.stem}.v8_4_migration_copy{source_path.suffix}")


def _preflight(dry_run: dict, source_path: Path | None) -> list[dict]:
    exists = bool(source_path and source_path.exists())
    return [
        {"name": "SQLite source database detected", "status": "PASS" if source_path else "BLOCKED"},
        {"name": "Source database exists", "status": "PASS" if exists else "CHECK MANUALLY"},
        {"name": "Dry-run SQL available", "status": "PASS" if dry_run["statement_count"] else "NO SQL NEEDED"},
        {"name": "Original DB protection", "status": "PASS - copy only"},
    ]


def _copy_apply_steps(source_path: Path | None, copy_path: Path | None, dry_run: dict) -> list[str]:
    if not source_path or not copy_path:
        return ["Configure a local SQLite database before using the copy migration assistant."]
    if not dry_run["statement_count"]:
        return ["No migration SQL is needed. Run post_migration_verify.py on the current database."]
    return [
        "Stop the app before copying the database.",
        f"Copy {source_path} to {copy_path}.",
        "Apply generated SQL only to the copied database.",
        "Run post-migration verification against the copied database.",
        "Run rollback drill before touching the real database.",
    ]


def _commands(source_path: Path | None, copy_path: Path | None) -> list[str]:
    if not source_path or not copy_path:
        return ["SQLite database path is required."]
    return [
        f"python scripts/safe_copy_migration_apply.py {source_path} {copy_path}",
        f"python scripts/post_migration_verify.py {copy_path}",
        f"python scripts/rollback_drill.py {source_path}",
    ]


def _rollback_steps(source_path: Path | None, copy_path: Path | None) -> list[str]:
    if not source_path or not copy_path:
        return ["Configure SQLite first, then run rollback drill on a copied database."]
    return [
        "Create a temporary backup copy of the original database.",
        "Create a migration copy and apply migration SQL there.",
        "Restore the backup into a rollback copy.",
        "Verify rollback copy checksum equals the original backup checksum.",
        "Verify the original database was not modified.",
    ]


def _rollback_commands(source_path: Path | None, copy_path: Path | None) -> list[str]:
    if not source_path or not copy_path:
        return ["SQLite database path is required."]
    return [f"python scripts/rollback_drill.py {source_path}"]


def _success_criteria() -> list[str]:
    return [
        "Copy migration exits with code 0 or reports no SQL needed.",
        "Post-migration verification on the copy is VERIFIED.",
        "Rollback drill checksum comparison passes.",
        "Original database timestamp and checksum stay unchanged.",
    ]


def _sql_script(statements: list[dict]) -> str:
    if not statements:
        return "-- No SQL needed for current schema.\n"
    lines = ["BEGIN TRANSACTION;"]
    lines.extend(row["sql"].rstrip() for row in statements)
    lines.append("COMMIT;")
    return "\n".join(lines).strip() + "\n"


def _copy_apply_markdown(data: dict) -> str:
    lines = ["# v8.4 Safe Migration Apply on Copied Database", "", f"Status: {data['status']}", f"Will modify original DB: {data['will_modify_original_database']}", "", "## Commands"]
    lines.extend(f"```bash\n{command}\n```" for command in data["commands"])
    lines.extend(["", "## Copy apply steps"])
    lines.extend(f"- [ ] {step}" for step in data["copy_apply_steps"])
    return "\n".join(lines).strip() + "\n"


def _rollback_markdown(data: dict) -> str:
    lines = ["# v8.4 Rollback Drill Automation", "", f"Status: {data['status']}", f"Will modify original DB: {data['will_modify_original_database']}", "", "## Drill steps"]
    lines.extend(f"- [ ] {step}" for step in data["drill_steps"])
    lines.extend(["", "## Success criteria"])
    lines.extend(f"- {item}" for item in data["success_criteria"])
    return "\n".join(lines).strip() + "\n"
