from __future__ import annotations

from sqlalchemy.orm import Session

from app.profile_manual_restore_service import restore_approval_phrase, v10_8_restore_audit_trail
from app.profile_reset_orchestrator_service import approval_phrase as profile_reset_approval_phrase
from app.profile_reset_snapshot_service import (
    v10_6_profile_reset_audit_trail,
    v10_6_rollback_snapshot_export,
)
from app.profile_restore_conflict_service import (
    v10_9_guarded_restore_plan,
    v10_9_operator_restore_conflict_package,
    v10_9_restore_conflict_report,
    v10_9_restore_digest_lock_audit_trail,
)
from app.profile_rollback_rehearsal_service import (
    v10_7_manual_rollback_import_rehearsal,
    v10_7_restore_checklist,
)


def v11_0_restore_governance_stability_report(
    db: Session,
    profile_id: str = "core-risk",
    snapshot_export: dict | None = None,
) -> dict:
    source = snapshot_export or v10_6_rollback_snapshot_export(db, profile_id)
    conflict = v10_9_restore_conflict_report(db, profile_id, source)
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id, source)
    reset_audit = v10_6_profile_reset_audit_trail(db, profile_id)
    restore_audit = v10_8_restore_audit_trail(db, profile_id)
    digest_audit = v10_9_restore_digest_lock_audit_trail(db, profile_id)
    gates = _stability_gates(conflict, rehearsal, reset_audit, restore_audit, digest_audit)
    ready = all(item["ready"] for item in gates)
    data = {
        "version": "11.0",
        "mode": "restore-governance-stabilization",
        "status": "Stable recovery governance ready" if ready else "Recovery governance needs attention",
        "ready": ready,
        "profile_id": profile_id,
        "snapshot_digest_lock_required": conflict["snapshot_digest_lock_required"],
        "reset_approval_phrase": profile_reset_approval_phrase(profile_id),
        "restore_approval_phrase": restore_approval_phrase(profile_id),
        "stability_gates": gates,
        "conflict_summary": _conflict_summary(conflict),
        "rehearsal_ready": rehearsal["ready"],
        "audit_summary": _audit_summary(reset_audit, restore_audit, digest_audit),
    }
    data["content"] = _stability_markdown(data)
    return data


def v11_0_final_operator_recovery_runbook(
    db: Session,
    profile_id: str = "core-risk",
    snapshot_export: dict | None = None,
) -> dict:
    report = v11_0_restore_governance_stability_report(db, profile_id, snapshot_export)
    plan = v10_9_guarded_restore_plan(db, profile_id, snapshot_export)
    checklist = v10_7_restore_checklist(profile_id)
    data = {
        "version": "11.0",
        "mode": "final-operator-recovery-runbook",
        "status": "Runbook ready" if report["ready"] else "Runbook generated with warnings",
        "ready": report["ready"],
        "profile_id": profile_id,
        "required_inputs": _required_inputs(report),
        "recovery_sequence": _recovery_sequence(),
        "stability_report": report,
        "guarded_restore_plan": plan,
        "restore_checklist": checklist,
    }
    data["content"] = _runbook_markdown(data)
    return data


def v11_0_operator_recovery_package(db: Session, profile_id: str = "core-risk") -> dict:
    stability = v11_0_restore_governance_stability_report(db, profile_id)
    runbook = v11_0_final_operator_recovery_runbook(db, profile_id)
    conflict_package = v10_9_operator_restore_conflict_package(db, profile_id)
    data = {
        "version": "11.0",
        "mode": "operator-recovery-package",
        "status": runbook["status"],
        "ready": runbook["ready"],
        "profile_id": profile_id,
    }
    data["content"] = "# v11.0 Final Operator Recovery Package\n\n" + "\n\n".join(
        [stability["content"], runbook["content"], conflict_package["content"]]
    )
    return data


def _stability_gates(
    conflict: dict, rehearsal: dict, reset_audit: dict, restore_audit: dict, digest_audit: dict
) -> list[dict]:
    critical = [item for item in conflict["conflicts"] if item.get("severity") == "critical"]
    return [
        {"id": "snapshot-ready", "ready": rehearsal["ready"], "detail": rehearsal["status"]},
        {
            "id": "digest-lock-present",
            "ready": bool(conflict["snapshot_digest_lock_required"]),
            "detail": conflict["snapshot_digest_lock_required"],
        },
        {"id": "no-critical-conflict", "ready": not critical, "detail": f"critical_conflicts={len(critical)}"},
        {
            "id": "reset-audit-readable",
            "ready": "audit_events" in reset_audit,
            "detail": f"events={len(reset_audit.get('audit_events', []))}",
        },
        {
            "id": "restore-audit-readable",
            "ready": "audit_events" in restore_audit,
            "detail": f"events={len(restore_audit.get('audit_events', []))}",
        },
        {
            "id": "digest-audit-readable",
            "ready": "audit_events" in digest_audit,
            "detail": f"events={len(digest_audit.get('audit_events', []))}",
        },
    ]


def _conflict_summary(conflict: dict) -> dict:
    levels: dict[str, int] = {}
    for item in conflict["conflicts"]:
        levels[item["severity"]] = levels.get(item["severity"], 0) + 1
    return {"status": conflict["status"], "count": len(conflict["conflicts"]), "by_severity": levels}


def _audit_summary(reset_audit: dict, restore_audit: dict, digest_audit: dict) -> dict:
    return {
        "reset_events": len(reset_audit.get("audit_events", [])),
        "restore_events": len(restore_audit.get("audit_events", [])),
        "digest_lock_events": len(digest_audit.get("audit_events", [])),
    }


def _required_inputs(report: dict) -> list[str]:
    return [
        "v10.6 rollback snapshot JSON",
        f"reset phrase: {report['reset_approval_phrase']}",
        f"restore phrase: {report['restore_approval_phrase']}",
        f"snapshot digest lock: {report['snapshot_digest_lock_required']}",
        "operator name for audit trail",
    ]


def _recovery_sequence() -> list[str]:
    return [
        "Export or load the v10.6 rollback snapshot.",
        "Run v10.7 rollback import rehearsal and resolve any blocking result.",
        "Review the v10.9 conflict report and copy the exact digest lock.",
        "Execute v10.9 restore with restore phrase, digest lock, and operator name.",
        "Review v10.8 and v10.9 audit trails after the restore.",
    ]


def _stability_markdown(data: dict) -> str:
    lines = [
        "# v11.0 Restore Governance Stability Report",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        f"Digest lock: `{data['snapshot_digest_lock_required']}`",
        "",
        "## Stability Gates",
    ]
    for gate in data["stability_gates"]:
        mark = "PASS" if gate["ready"] else "BLOCKED"
        lines.append(f"- {mark}: {gate['id']} — {gate['detail']}")
    return "\n".join(lines).strip() + "\n"


def _runbook_markdown(data: dict) -> str:
    lines = [
        "# v11.0 Final Operator Recovery Runbook",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        "",
        "## Required Inputs",
    ]
    lines.extend(f"- {item}" for item in data["required_inputs"])
    lines.append("")
    lines.append("## Recovery Sequence")
    for index, item in enumerate(data["recovery_sequence"], start=1):
        lines.append(f"{index}. {item}")
    return "\n".join(lines).strip() + "\n"
