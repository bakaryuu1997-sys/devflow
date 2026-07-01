from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import ActivityLog, Project
from app.profile_rollback_rehearsal_service import v10_7_manual_rollback_import_rehearsal
from app.sample_project_builder_data import SAMPLE_PROFILE_SEEDS

RESTORE_AUDIT_ACTION = "v10_8_guarded_manual_restore"


def restore_approval_phrase(profile_id: str) -> str:
    return f"RESTORE DEMO PROFILE: {profile_id}"


def v10_8_guarded_restore_plan(db: Session, profile_id: str = "core-risk", snapshot_export: dict | None = None) -> dict:
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id, snapshot_export)
    data = {
        "version": "10.8",
        "mode": "guarded-manual-restore-plan",
        "status": "Ready" if rehearsal["ready"] else "Blocked",
        "ready": rehearsal["ready"],
        "profile_id": profile_id,
        "restore_approval_phrase": restore_approval_phrase(profile_id),
        "snapshot_digest": rehearsal["snapshot_digest"],
        "rehearsal_validation": rehearsal["validation"],
        "guardrails": _guardrails(),
    }
    data["content"] = _plan_markdown(data)
    return data


def v10_8_execute_guarded_manual_restore(
    db: Session,
    profile_id: str = "core-risk",
    restore_approval: str = "",
    operator_name: str = "",
    snapshot_export: dict | None = None,
) -> dict:
    expected = restore_approval_phrase(profile_id)
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id, snapshot_export)
    if restore_approval != expected:
        return _blocked(profile_id, expected, rehearsal, "Second approval phrase required")
    if not rehearsal["ready"]:
        return _blocked(profile_id, expected, rehearsal, "Restore rehearsal blocked")
    snapshot = (snapshot_export or {}).get("snapshot") or _current_snapshot_from_rehearsal(db, profile_id)
    before_counts = _current_counts(db, profile_id)
    deleted = _delete_current_profile_rows(db, profile_id)
    restored = _insert_snapshot_rows(db, snapshot)
    db.commit()
    after_counts = _current_counts(db, profile_id)
    audit = _write_restore_audit(db, profile_id, operator_name, rehearsal, before_counts, after_counts, restored)
    data = {
        "version": "10.8",
        "mode": "guarded-manual-restore-execution",
        "status": "Restore complete",
        "ready": True,
        "profile_id": profile_id,
        "snapshot_digest": rehearsal["snapshot_digest"],
        "deleted_records": deleted,
        "restored_records": restored,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "audit_event": audit,
    }
    data["content"] = _execute_markdown(data)
    return data


def v10_8_restore_audit_trail(db: Session, profile_id: str = "core-risk") -> dict:
    rows = db.scalars(
        select(ActivityLog).where(ActivityLog.action == RESTORE_AUDIT_ACTION).order_by(ActivityLog.id.desc())
    ).all()
    events = [_decode_event(row) for row in rows]
    data = {
        "version": "10.8",
        "mode": "guarded-manual-restore-audit-trail",
        "status": "Audit trail ready",
        "ready": True,
        "profile_id": profile_id,
        "audit_events": [event for event in events if event.get("profile_id") == profile_id],
    }
    data["content"] = _audit_markdown(data)
    return data


def v10_8_operator_restore_execution_package(db: Session, profile_id: str = "core-risk") -> dict:
    plan = v10_8_guarded_restore_plan(db, profile_id)
    audit = v10_8_restore_audit_trail(db, profile_id)
    data = {
        "version": "10.8",
        "mode": "operator-restore-execution-package",
        "status": plan["status"],
        "ready": plan["ready"],
    }
    data["content"] = "# v10.8 Operator Restore Execution Package\n\n" + "\n\n".join(
        [plan["content"], audit["content"]]
    )
    return data


def _current_snapshot_from_rehearsal(db: Session, profile_id: str) -> dict:
    from app.profile_reset_snapshot_service import v10_6_rollback_snapshot_export

    return v10_6_rollback_snapshot_export(db, profile_id)["snapshot"]


def _delete_current_profile_rows(db: Session, profile_id: str) -> dict:
    seed = SAMPLE_PROFILE_SEEDS[profile_id]
    project = db.scalars(select(Project).where(Project.name == seed["project"][0])).first()
    if not project:
        return {"projects": 0}
    deleted: dict[str, int] = {}
    for table in reversed(Base.metadata.sorted_tables):
        if "project_id" in table.c:
            result = db.execute(delete(table).where(table.c.project_id == project.id))
            if result.rowcount:
                deleted[table.name] = result.rowcount
    result = db.execute(delete(Project).where(Project.id == project.id))
    deleted["projects"] = result.rowcount or 0
    db.flush()
    return deleted


def _insert_snapshot_rows(db: Session, snapshot: dict) -> dict:
    counts: dict[str, int] = {}
    tables = snapshot.get("tables", {})
    for table in Base.metadata.sorted_tables:
        rows = tables.get(table.name, [])
        if not rows:
            continue
        clean_rows = [_coerce_row(table, row) for row in rows]
        db.execute(table.insert(), clean_rows)
        counts[table.name] = len(clean_rows)
    return counts


def _coerce_row(table, row: dict) -> dict:
    clean = {key: row[key] for key in row if key in table.c}
    for col in table.c:
        if (
            col.name in clean
            and getattr(col.type, "python_type", None) is datetime
            and isinstance(clean[col.name], str)
        ):
            clean[col.name] = datetime.fromisoformat(clean[col.name])
    return clean


def _current_counts(db: Session, profile_id: str) -> dict:
    seed = SAMPLE_PROFILE_SEEDS.get(profile_id)
    project = db.scalars(select(Project).where(Project.name == seed["project"][0])).first() if seed else None
    if not project:
        return {}
    counts = {"projects": 1}
    for table in Base.metadata.sorted_tables:
        if table.name == "projects" or "project_id" not in table.c:
            continue
        rows = db.execute(select(table.c.id).where(table.c.project_id == project.id)).all()
        if rows:
            counts[table.name] = len(rows)
    return counts


def _write_restore_audit(
    db: Session, profile_id: str, operator_name: str, rehearsal: dict, before: dict, after: dict, restored: dict
) -> dict:
    event = {
        "profile_id": profile_id,
        "operator_name": operator_name or "unknown",
        "snapshot_digest": rehearsal["snapshot_digest"],
        "before_counts": before,
        "after_counts": after,
        "restored_records": restored,
    }
    db.add(
        ActivityLog(
            project_id=None,
            action=RESTORE_AUDIT_ACTION,
            message=json.dumps(event, default=_json_default, sort_keys=True),
        )
    )
    db.commit()
    event["audit_digest"] = _digest(event)
    return event


def _blocked(profile_id: str, expected: str, rehearsal: dict, status: str) -> dict:
    data = {
        "version": "10.8",
        "mode": "guarded-manual-restore-execution",
        "status": status,
        "ready": False,
        "profile_id": profile_id,
        "expected_restore_approval_phrase": expected,
        "rehearsal_ready": rehearsal.get("ready", False),
    }
    data["content"] = f"# v10.8 Restore Blocked\n\nStatus: {status}\nExpected phrase: `{expected}`\n"
    return data


def _decode_event(row: ActivityLog) -> dict:
    data = json.loads(row.message)
    data["audit_id"] = row.id
    data["created_at"] = _json_default(row.created_at)
    return data


def _guardrails() -> list[str]:
    return [
        "v10.8 requires the v10.7 rehearsal to be ready before restore.",
        "Restore uses a second phrase distinct from demo reset approval.",
        "The restore is profile-scoped and writes an ActivityLog audit event.",
    ]


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, default=_json_default, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _plan_markdown(data: dict) -> str:
    lines = [
        "# v10.8 Guarded Manual Restore Plan",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        f"Restore phrase: `{data['restore_approval_phrase']}`",
        f"Snapshot digest: `{data['snapshot_digest']}`",
        "",
        "## Guardrails",
    ]
    lines.extend(f"- {item}" for item in data["guardrails"])
    return "\n".join(lines).strip() + "\n"


def _execute_markdown(data: dict) -> str:
    return f"# v10.8 Guarded Manual Restore Result\n\nStatus: {data['status']}\nProfile: {data['profile_id']}\nDigest: `{data['snapshot_digest']}`\n"


def _audit_markdown(data: dict) -> str:
    lines = ["# v10.8 Manual Restore Audit Trail", "", f"Profile: {data['profile_id']}"]
    if not data["audit_events"]:
        lines.append("No manual restore events recorded yet.")
    for event in data["audit_events"]:
        lines.append(f"- Audit #{event['audit_id']}: digest `{event['snapshot_digest']}` by {event['operator_name']}")
    return "\n".join(lines).strip() + "\n"
