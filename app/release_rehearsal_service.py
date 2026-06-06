from __future__ import annotations

from sqlalchemy.orm import Session

from app.migration_checker_service import local_database_migration_check, upgrade_safety_report
from app.migration_copy_apply_service import rollback_drill_automation_plan, safe_copy_migration_apply_assistant
from app.production_migration_gate_service import APPROVAL_PHRASE, final_production_upgrade_checklist


def production_upgrade_rehearsal_report(db: Session) -> dict:
    migration = local_database_migration_check(db)
    safety = upgrade_safety_report(db)
    copy_plan = safe_copy_migration_apply_assistant(db)
    rollback = rollback_drill_automation_plan(db)
    checklist = final_production_upgrade_checklist(db)
    readiness = _rehearsal_readiness(migration, safety, copy_plan, rollback)
    data = {
        "version": "8.7",
        "mode": "production-upgrade-rehearsal-report",
        "status": readiness["status"],
        "rehearsal_score": readiness["score"],
        "summary": readiness["summary"],
        "evidence": _evidence_rows(migration, safety, copy_plan, rollback),
        "rehearsal_steps": _rehearsal_steps(copy_plan, rollback, checklist),
        "operator_findings": _operator_findings(migration, safety),
        "go_no_go": readiness["go_no_go"],
    }
    data["content"] = _rehearsal_markdown(data)
    return data


def operator_signoff_checklist(db: Session) -> dict:
    rehearsal = production_upgrade_rehearsal_report(db)
    checklist = final_production_upgrade_checklist(db)
    data = {
        "version": "8.7",
        "mode": "operator-signoff-checklist",
        "status": _signoff_status(rehearsal),
        "approval_phrase": APPROVAL_PHRASE,
        "required_signoffs": _required_signoffs(rehearsal, checklist),
        "operator_attestations": _operator_attestations(),
        "blocked_until": _blocked_until(rehearsal),
        "rehearsal_report": rehearsal,
    }
    data["content"] = _signoff_markdown(data)
    return data


def _rehearsal_readiness(migration: dict, safety: dict, copy_plan: dict, rollback: dict) -> dict:
    blockers = []
    if migration.get("status") not in {"Ready", "Already migrated"}:
        blockers.append("Migration checker has pending schema work.")
    if safety.get("risk_score", 100) >= 80:
        blockers.append("Upgrade safety risk score is too high.")
    if not copy_plan.get("commands"):
        blockers.append("Safe copy migration command is missing.")
    if not rollback.get("commands"):
        blockers.append("Rollback drill command is missing.")
    score = max(0, 100 - len(blockers) * 25)
    return {
        "status": "Ready for Operator Sign-off" if not blockers else "Rehearsal Blocked",
        "score": score,
        "summary": blockers or ["Rehearsal evidence is ready for operator review."],
        "go_no_go": "GO for sign-off review" if not blockers else "NO-GO until blockers are resolved",
    }


def _evidence_rows(migration: dict, safety: dict, copy_plan: dict, rollback: dict) -> list[dict]:
    return [
        {"name": "Migration check", "status": migration.get("status", "unknown")},
        {"name": "Upgrade safety", "status": safety.get("status", "unknown")},
        {"name": "Safe copy apply", "status": "Planned" if copy_plan.get("commands") else "Missing"},
        {"name": "Rollback drill", "status": "Planned" if rollback.get("commands") else "Missing"},
    ]


def _rehearsal_steps(copy_plan: dict, rollback: dict, checklist: dict) -> list[dict]:
    return [
        {"name": "1. Confirm production backup", "items": checklist.get("sections", [{}])[0].get("items", [])},
        {"name": "2. Apply migration on copied database", "items": copy_plan.get("commands", [])},
        {"name": "3. Run rollback drill", "items": rollback.get("commands", [])},
        {"name": "4. Capture operator notes", "items": ["Record start time", "Record command outputs", "Record final go/no-go decision"]},
    ]


def _operator_findings(migration: dict, safety: dict) -> list[str]:
    findings = [f"Migration status: {migration.get('status', 'unknown')}"]
    findings.append(f"Upgrade safety status: {safety.get('status', 'unknown')}")
    findings.append(f"Risk score: {safety.get('risk_score', 'unknown')}")
    return findings


def _signoff_status(rehearsal: dict) -> str:
    return "Ready for Signature" if rehearsal["status"] == "Ready for Operator Sign-off" else "Blocked"


def _required_signoffs(rehearsal: dict, checklist: dict) -> list[dict]:
    return [
        {"role": "Operator", "item": "I ran the rehearsal commands on a copy database.", "required": True},
        {"role": "Operator", "item": "I verified rollback drill output and preserved backups.", "required": True},
        {"role": "Reviewer", "item": checklist.get("final_go_no_go", "Review final production checklist."), "required": True},
        {"role": "Approver", "item": f"I understand real migration requires `{APPROVAL_PHRASE}`.", "required": True},
    ]


def _operator_attestations() -> list[str]:
    return [
        "Database backup path recorded",
        "Safe-copy migration passed",
        "Rollback drill passed",
        "Post-migration verification command prepared",
        "Production window and owner confirmed",
    ]


def _blocked_until(rehearsal: dict) -> list[str]:
    if rehearsal["status"] == "Ready for Operator Sign-off":
        return []
    return rehearsal.get("summary", [])


def _rehearsal_markdown(data: dict) -> str:
    lines = ["# v8.7 Production Upgrade Rehearsal Report", "", f"Status: {data['status']}", f"Score: {data['rehearsal_score']}", f"Decision: {data['go_no_go']}", ""]
    lines.extend(["## Evidence"] + [f"- {row['name']}: {row['status']}" for row in data["evidence"]] + [""])
    for step in data["rehearsal_steps"]:
        lines.append(f"## {step['name']}")
        lines.extend(f"- [ ] {item}" for item in (step["items"] or ["No items."]))
        lines.append("")
    lines.extend(["## Operator findings"] + [f"- {item}" for item in data["operator_findings"]])
    return "\n".join(lines).strip() + "\n"


def _signoff_markdown(data: dict) -> str:
    lines = ["# v8.7 Operator Sign-off Checklist", "", f"Status: {data['status']}", f"Approval phrase: `{data['approval_phrase']}`", "", "## Required sign-offs"]
    lines.extend(f"- [ ] {row['role']}: {row['item']}" for row in data["required_signoffs"])
    lines.extend(["", "## Operator attestations"])
    lines.extend(f"- [ ] {item}" for item in data["operator_attestations"])
    if data["blocked_until"]:
        lines.extend(["", "## Blocked until"])
        lines.extend(f"- {item}" for item in data["blocked_until"])
    return "\n".join(lines).strip() + "\n"
