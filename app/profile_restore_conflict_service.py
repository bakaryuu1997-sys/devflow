from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActivityLog
from app.profile_manual_restore_service import restore_approval_phrase, v10_8_execute_guarded_manual_restore
from app.profile_reset_snapshot_service import v10_6_rollback_snapshot_export
from app.profile_rollback_rehearsal_service import v10_7_manual_rollback_import_rehearsal

DIGEST_LOCK_AUDIT_ACTION = "v10_9_restore_digest_lock"


def v10_9_restore_conflict_report(db: Session, profile_id: str = "core-risk", snapshot_export: dict | None = None) -> dict:
    source = snapshot_export or v10_6_rollback_snapshot_export(db, profile_id)
    snapshot = source.get("snapshot", source)
    current = v10_6_rollback_snapshot_export(db, profile_id).get("snapshot", {})
    snapshot_digest = _digest(snapshot)
    current_digest = _digest(current)
    conflicts = _detect_conflicts(snapshot, current)
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id, source)
    data = {
        "version": "10.9",
        "mode": "restore-conflict-detection",
        "status": "Conflict detected" if conflicts else "No restore conflict detected",
        "ready": rehearsal["ready"],
        "profile_id": profile_id,
        "snapshot_digest": snapshot_digest,
        "current_digest": current_digest,
        "snapshot_digest_lock_required": snapshot_digest,
        "conflicts": conflicts,
        "table_count_delta": _count_delta(snapshot, current),
        "rehearsal_ready": rehearsal["ready"],
    }
    data["content"] = _conflict_markdown(data)
    return data


def v10_9_guarded_restore_plan(db: Session, profile_id: str = "core-risk", snapshot_export: dict | None = None) -> dict:
    report = v10_9_restore_conflict_report(db, profile_id, snapshot_export)
    data = {
        "version": "10.9",
        "mode": "restore-plan-with-digest-lock",
        "status": "Ready with digest lock" if report["ready"] else "Blocked",
        "ready": report["ready"],
        "profile_id": profile_id,
        "restore_approval_phrase": restore_approval_phrase(profile_id),
        "snapshot_digest_lock_required": report["snapshot_digest_lock_required"],
        "conflict_report": report,
        "guardrails": _guardrails(),
    }
    data["content"] = _plan_markdown(data)
    return data


def v10_9_execute_guarded_manual_restore(
    db: Session,
    profile_id: str = "core-risk",
    restore_approval: str = "",
    operator_name: str = "",
    snapshot_digest_lock: str = "",
    snapshot_export: dict | None = None,
) -> dict:
    report = v10_9_restore_conflict_report(db, profile_id, snapshot_export)
    expected_lock = report["snapshot_digest_lock_required"]
    if snapshot_digest_lock != expected_lock:
        return _blocked(profile_id, report, "Snapshot digest lock required")
    result = v10_8_execute_guarded_manual_restore(db, profile_id, restore_approval, operator_name, snapshot_export)
    if result.get("ready"):
        result = dict(result)
        result["version"] = "10.9"
        result["mode"] = "guarded-restore-with-digest-lock"
        result["snapshot_digest_lock"] = snapshot_digest_lock
        result["conflicts_acknowledged"] = report["conflicts"]
        result["digest_lock_audit_event"] = _write_digest_lock_audit(db, profile_id, operator_name, report)
        result["content"] = _execute_markdown(result)
    return result


def v10_9_restore_digest_lock_audit_trail(db: Session, profile_id: str = "core-risk") -> dict:
    rows = db.scalars(select(ActivityLog).where(ActivityLog.action == DIGEST_LOCK_AUDIT_ACTION).order_by(ActivityLog.id.desc())).all()
    events = [_decode_event(row) for row in rows]
    filtered = [event for event in events if event.get("profile_id") == profile_id]
    data = {"version": "10.9", "mode": "restore-digest-lock-audit", "status": "Audit trail ready", "ready": True, "profile_id": profile_id, "audit_events": filtered}
    data["content"] = _audit_markdown(data)
    return data


def v10_9_operator_restore_conflict_package(db: Session, profile_id: str = "core-risk") -> dict:
    report = v10_9_restore_conflict_report(db, profile_id)
    plan = v10_9_guarded_restore_plan(db, profile_id)
    audit = v10_9_restore_digest_lock_audit_trail(db, profile_id)
    data = {"version": "10.9", "mode": "operator-restore-conflict-package", "status": plan["status"], "ready": plan["ready"], "profile_id": profile_id}
    data["content"] = "# v10.9 Operator Restore Conflict Package\n\n" + "\n\n".join([report["content"], plan["content"], audit["content"]])
    return data


def _detect_conflicts(snapshot: dict, current: dict) -> list[dict]:
    conflicts: list[dict] = []
    if not current.get("ready"):
        conflicts.append({"type": "current_project_missing", "severity": "medium", "detail": current.get("status", "Current profile project is missing")})
    if snapshot.get("profile_id") != current.get("profile_id"):
        conflicts.append({"type": "profile_mismatch", "severity": "critical", "detail": "Snapshot profile differs from current profile."})
    for table, delta in _count_delta(snapshot, current).items():
        if delta["snapshot"] != delta["current"]:
            conflicts.append({"type": "table_count_delta", "severity": "high", "table": table, "snapshot": delta["snapshot"], "current": delta["current"]})
    if snapshot.get("ready") and current.get("ready") and _digest(snapshot) != _digest(current):
        conflicts.append({"type": "row_digest_delta", "severity": "high", "detail": "Current rows differ from the locked snapshot."})
    return conflicts


def _count_delta(snapshot: dict, current: dict) -> dict:
    left = _counts(snapshot.get("tables", {})) if isinstance(snapshot, dict) else {}
    right = _counts(current.get("tables", {})) if isinstance(current, dict) else {}
    names = sorted(set(left) | set(right))
    return {name: {"snapshot": left.get(name, 0), "current": right.get(name, 0)} for name in names}


def _counts(tables: dict) -> dict:
    return {name: len(rows) for name, rows in tables.items()}


def _blocked(profile_id: str, report: dict, status: str) -> dict:
    data = {"version": "10.9", "mode": "guarded-restore-with-digest-lock", "status": status, "ready": False, "profile_id": profile_id, "expected_snapshot_digest_lock": report["snapshot_digest_lock_required"], "conflicts": report["conflicts"]}
    data["content"] = f"# v10.9 Restore Blocked\n\nStatus: {status}\nExpected snapshot digest lock: `{report['snapshot_digest_lock_required']}`\n"
    return data


def _write_digest_lock_audit(db: Session, profile_id: str, operator_name: str, report: dict) -> dict:
    event = {"profile_id": profile_id, "operator_name": operator_name or "unknown", "snapshot_digest_lock": report["snapshot_digest_lock_required"], "current_digest": report["current_digest"], "conflict_count": len(report["conflicts"])}
    db.add(ActivityLog(project_id=None, action=DIGEST_LOCK_AUDIT_ACTION, message=json.dumps(event, sort_keys=True)))
    db.commit()
    event["audit_digest"] = _digest(event)
    return event


def _decode_event(row: ActivityLog) -> dict:
    data = json.loads(row.message)
    data["audit_id"] = row.id
    data["created_at"] = _json_default(row.created_at)
    return data


def _guardrails() -> list[str]:
    return ["A restore must include the v10.8 restore phrase.", "The operator must also submit the exact snapshot digest lock.", "Conflict detection runs before restore and is written to audit after success."]


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, default=_json_default, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _conflict_markdown(data: dict) -> str:
    lines = ["# v10.9 Restore Conflict Detection", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", f"Snapshot digest lock: `{data['snapshot_digest_lock_required']}`", "", "## Conflicts"]
    if not data["conflicts"]:
        lines.append("- None detected.")
    for item in data["conflicts"]:
        lines.append(f"- {item['severity']}: {item['type']}")
    return "\n".join(lines).strip() + "\n"


def _plan_markdown(data: dict) -> str:
    lines = ["# v10.9 Guarded Restore Plan With Digest Lock", "", f"Status: {data['status']}", f"Restore phrase: `{data['restore_approval_phrase']}`", f"Digest lock: `{data['snapshot_digest_lock_required']}`", "", "## Guardrails"]
    lines.extend(f"- {item}" for item in data["guardrails"])
    return "\n".join(lines).strip() + "\n"


def _execute_markdown(data: dict) -> str:
    return f"# v10.9 Guarded Restore Result\n\nStatus: {data['status']}\nProfile: {data['profile_id']}\nDigest lock: `{data['snapshot_digest_lock']}`\n"


def _audit_markdown(data: dict) -> str:
    lines = ["# v10.9 Restore Digest Lock Audit", "", f"Profile: {data['profile_id']}"]
    if not data["audit_events"]:
        lines.append("No digest lock restore events recorded yet.")
    for event in data["audit_events"]:
        lines.append(f"- Audit #{event['audit_id']}: lock `{event['snapshot_digest_lock']}` by {event['operator_name']}")
    return "\n".join(lines).strip() + "\n"
