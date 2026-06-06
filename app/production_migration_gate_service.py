from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.migration_apply_assistant_service import post_migration_verification_snapshot
from app.migration_checker_service import upgrade_safety_report
from app.migration_copy_apply_service import rollback_drill_automation_plan, safe_copy_migration_apply_assistant
from app.migration_sql_service import backup_checklist, dry_run_sql_migration

APPROVAL_PHRASE = "I_APPROVE_PRODUCTION_MIGRATION"


def human_approved_real_migration_gate(db: Session) -> dict:
    dry_run = dry_run_sql_migration(db)
    safety = upgrade_safety_report(db)
    copy_plan = safe_copy_migration_apply_assistant(db)
    rollback = rollback_drill_automation_plan(db)
    source_path = _sqlite_path()
    blockers = _gate_blockers(dry_run, source_path)
    data = {
        "version": "8.5",
        "mode": "human-approved-real-migration-gate",
        "status": "Approval Required" if not blockers else "Blocked",
        "will_modify_original_database": True,
        "approval_phrase": APPROVAL_PHRASE,
        "source_database": str(source_path) if source_path else "non-sqlite-or-unknown",
        "statement_count": dry_run["statement_count"],
        "blockers": blockers,
        "required_evidence": _required_evidence(),
        "approval_commands": _approval_commands(source_path),
        "rollback_commands": _rollback_commands(source_path),
        "safety_report": safety,
        "safe_copy_plan": copy_plan,
        "rollback_drill_plan": rollback,
    }
    data["content"] = _gate_markdown(data)
    return data


def final_production_upgrade_checklist(db: Session) -> dict:
    verify = post_migration_verification_snapshot(db)
    backup = backup_checklist(db)
    gate = human_approved_real_migration_gate(db)
    data = {
        "version": "8.5",
        "mode": "final-production-upgrade-checklist",
        "status": "Ready for Human Review",
        "sections": _checklist_sections(gate),
        "backup_checklist": backup,
        "post_migration_verification": verify,
        "approval_phrase": APPROVAL_PHRASE,
        "final_go_no_go": _go_no_go(gate),
    }
    data["content"] = _checklist_markdown(data)
    return data


def _sqlite_path() -> Path | None:
    url = settings.database_url
    if not url.startswith("sqlite:///"):
        return None
    return Path(url.replace("sqlite:///", "", 1)).resolve()


def _gate_blockers(dry_run: dict, source_path: Path | None) -> list[str]:
    blockers: list[str] = []
    if source_path is None:
        blockers.append("A local SQLite database is required for this guided gate.")
    elif not source_path.exists():
        blockers.append("The configured SQLite database file does not exist.")
    if dry_run["statement_count"] == 0:
        blockers.append("No migration SQL is pending for the current schema.")
    return blockers


def _required_evidence() -> list[str]:
    return [
        "Fresh backup file exists outside the app folder.",
        "Safe copy migration returned COPY MIGRATION VERIFIED.",
        "Rollback drill returned ROLLBACK DRILL PASSED.",
        "Post-migration verification command is ready.",
        "Human approver typed the exact approval phrase.",
    ]


def _approval_commands(source_path: Path | None) -> list[str]:
    if not source_path:
        return ["Configure SQLite before running the real migration gate."]
    return [
        f"python scripts/real_migration_gate.py {source_path}",
        f"python scripts/real_migration_gate.py {source_path} --approve {APPROVAL_PHRASE}",
        f"python scripts/post_migration_verify.py {source_path}",
    ]


def _rollback_commands(source_path: Path | None) -> list[str]:
    if not source_path:
        return ["Rollback commands require a SQLite database path."]
    return [
        f"python scripts/rollback_drill.py {source_path}",
        "If production apply fails, stop the app and restore the newest .v8_5_prod_backup.db file.",
    ]


def _checklist_sections(gate: dict) -> list[dict]:
    return [
        {"name": "Pre-upgrade", "items": gate["required_evidence"][:3]},
        {"name": "Approval gate", "items": gate["required_evidence"][3:]},
        {"name": "Apply and verify", "items": gate["approval_commands"]},
        {"name": "Rollback readiness", "items": gate["rollback_commands"]},
    ]


def _go_no_go(gate: dict) -> str:
    if gate["blockers"]:
        return "NO-GO until blockers are resolved."
    return "GO only after backup, copy migration, rollback drill, and human approval all pass."


def _gate_markdown(data: dict) -> str:
    lines = ["# v8.5 Human-approved Real Migration Gate", "", f"Status: {data['status']}", "", "## Blockers"]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No automatic blockers detected."]))
    lines.extend(["", "## Required evidence"])
    lines.extend(f"- [ ] {item}" for item in data["required_evidence"])
    lines.extend(["", "## Approval commands"])
    lines.extend(f"```bash\n{command}\n```" for command in data["approval_commands"])
    return "\n".join(lines).strip() + "\n"


def _checklist_markdown(data: dict) -> str:
    lines = ["# v8.5 Final Production Upgrade Checklist", "", f"Decision: {data['final_go_no_go']}"]
    for section in data["sections"]:
        lines.extend(["", f"## {section['name']}"])
        lines.extend(f"- [ ] {item}" for item in section["items"])
    return "\n".join(lines).strip() + "\n"
