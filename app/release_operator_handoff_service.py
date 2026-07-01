from __future__ import annotations

from sqlalchemy.orm import Session

from app.migration_apply_assistant_service import post_migration_verification_snapshot
from app.migration_checker_service import upgrade_safety_report
from app.migration_copy_apply_service import rollback_drill_automation_plan, safe_copy_migration_apply_assistant
from app.production_migration_gate_service import (
    APPROVAL_PHRASE,
    final_production_upgrade_checklist,
    human_approved_real_migration_gate,
)


def production_upgrade_runbook(db: Session) -> dict:
    gate = human_approved_real_migration_gate(db)
    checklist = final_production_upgrade_checklist(db)
    copy_plan = safe_copy_migration_apply_assistant(db)
    rollback = rollback_drill_automation_plan(db)
    verify = post_migration_verification_snapshot(db)
    data = {
        "version": "8.6",
        "mode": "production-upgrade-runbook",
        "status": _runbook_status(gate),
        "source_database": gate.get("source_database", "unknown"),
        "approval_phrase": APPROVAL_PHRASE,
        "phases": _runbook_phases(gate, checklist, copy_plan, rollback, verify),
        "operator_commands": _operator_commands(gate),
        "go_no_go": checklist.get("final_go_no_go", "NO-GO until reviewed."),
    }
    data["content"] = _runbook_markdown(data)
    return data


def operator_handoff_package(db: Session) -> dict:
    runbook = production_upgrade_runbook(db)
    safety = upgrade_safety_report(db)
    manifest = _handoff_manifest(runbook, safety)
    data = {
        "version": "8.6",
        "mode": "operator-handoff-package",
        "status": "Ready for Operator Review",
        "package_name": "devflow_guard_v8_6_operator_handoff",
        "manifest": manifest,
        "required_files": _required_files(),
        "handoff_sections": _handoff_sections(runbook, safety),
        "runbook": runbook,
        "safety_report": safety,
    }
    data["content"] = _handoff_markdown(data)
    return data


def _runbook_status(gate: dict) -> str:
    if gate.get("blockers"):
        return "Blocked"
    return "Ready for Controlled Production Upgrade"


def _runbook_phases(gate: dict, checklist: dict, copy_plan: dict, rollback: dict, verify: dict) -> list[dict]:
    return [
        {"name": "1. Freeze and backup", "items": checklist["sections"][0]["items"]},
        {"name": "2. Prove migration on copy", "items": copy_plan.get("commands", [])},
        {"name": "3. Prove rollback", "items": rollback.get("commands", [])},
        {"name": "4. Human approval gate", "items": gate.get("approval_commands", [])},
        {"name": "5. Post-migration verification", "items": verify.get("recommended_next_steps", [])},
    ]


def _operator_commands(gate: dict) -> list[str]:
    commands = []
    commands.extend(gate.get("approval_commands", []))
    commands.extend(gate.get("rollback_commands", []))
    return commands


def _required_files() -> list[str]:
    return [
        "RUNBOOK.md",
        "OPERATOR_HANDOFF.md",
        "UPGRADE_COMMANDS.md",
        "ROLLBACK_DRILL.md",
        "POST_MIGRATION_VERIFY.md",
        "MANIFEST.md",
    ]


def _handoff_manifest(runbook: dict, safety: dict) -> dict:
    return {
        "version": "8.6",
        "source_database": runbook.get("source_database", "unknown"),
        "runbook_status": runbook["status"],
        "safety_status": safety.get("status", "unknown"),
        "approval_phrase_required": APPROVAL_PHRASE,
        "generated_for": "local SQLite production upgrade handoff",
    }


def _handoff_sections(runbook: dict, safety: dict) -> list[dict]:
    return [
        {
            "name": "Operator objective",
            "items": [
                "Upgrade an existing local SQLite database without touching it until human approval is explicit."
            ],
        },
        {
            "name": "Required evidence",
            "items": [
                "Backup exists",
                "Safe copy migration passed",
                "Rollback drill passed",
                "Post-migration verify command is ready",
            ],
        },
        {"name": "Runbook phases", "items": [phase["name"] for phase in runbook["phases"]]},
        {
            "name": "Safety status",
            "items": [safety.get("status", "unknown"), f"Risk score: {safety.get('risk_score', 'unknown')}"],
        },
    ]


def _runbook_markdown(data: dict) -> str:
    lines = [
        "# v8.6 Production Upgrade Runbook",
        "",
        f"Status: {data['status']}",
        f"Database: {data['source_database']}",
        "",
    ]
    lines.extend(["## Go / No-Go", data["go_no_go"], ""])
    for phase in data["phases"]:
        lines.extend([f"## {phase['name']}"])
        lines.extend(f"- [ ] {item}" for item in (phase["items"] or ["No items provided."]))
        lines.append("")
    lines.extend(["## Approval phrase", f"`{data['approval_phrase']}`"])
    return "\n".join(lines).strip() + "\n"


def _handoff_markdown(data: dict) -> str:
    lines = ["# v8.6 Operator Handoff Package", "", f"Package: {data['package_name']}", "", "## Manifest"]
    for key, value in data["manifest"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Required files"])
    lines.extend(f"- {item}" for item in data["required_files"])
    for section in data["handoff_sections"]:
        lines.extend(["", f"## {section['name']}"])
        lines.extend(f"- {item}" for item in section["items"])
    return "\n".join(lines).strip() + "\n"
