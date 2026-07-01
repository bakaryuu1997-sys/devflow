from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import ActivityLog, Project
from app.profile_reset_orchestrator_service import approval_phrase, v10_5_execute_profile_reset
from app.sample_project_builder_data import SAMPLE_PROFILE_SEEDS

AUDIT_ACTION = "v10_6_profile_reset_audit"


def v10_6_rollback_snapshot_export(db: Session, profile_id: str = "core-risk") -> dict:
    snapshot = _snapshot_profile_project(db, profile_id)
    data = {
        "version": "10.6",
        "mode": "profile-reset-rollback-snapshot-export",
        "status": "Snapshot ready" if snapshot["ready"] else snapshot["status"],
        "ready": snapshot["ready"],
        "profile_id": profile_id,
        "snapshot_digest": _digest(snapshot),
        "snapshot": snapshot,
    }
    data["content"] = _snapshot_markdown(data)
    return data


def v10_6_execute_profile_reset_with_audit(
    db: Session,
    profile_id: str = "core-risk",
    approval: str = "",
    operator_name: str = "",
) -> dict:
    expected = approval_phrase(profile_id)
    if approval != expected:
        result = v10_5_execute_profile_reset(db, profile_id, approval, operator_name)
        return _with_v106(result, None, None)
    before = _snapshot_profile_project(db, profile_id)
    result = v10_5_execute_profile_reset(db, profile_id, approval, operator_name)
    after = _snapshot_profile_project(db, profile_id)
    audit = _write_audit(db, profile_id, operator_name, before, after, result)
    return _with_v106(result, before, audit)


def v10_6_profile_reset_audit_trail(db: Session, profile_id: str = "core-risk") -> dict:
    rows = db.scalars(
        select(ActivityLog).where(ActivityLog.action == AUDIT_ACTION).order_by(ActivityLog.id.desc())
    ).all()
    events = [_decode_event(row) for row in rows]
    filtered = [event for event in events if event.get("profile_id") == profile_id]
    data = {
        "version": "10.6",
        "mode": "profile-reset-audit-trail",
        "status": "Audit trail ready",
        "ready": True,
        "profile_id": profile_id,
        "audit_events": filtered,
    }
    data["content"] = _audit_markdown(data)
    return data


def v10_6_operator_rollback_package(db: Session, profile_id: str = "core-risk") -> dict:
    snapshot = v10_6_rollback_snapshot_export(db, profile_id)
    audit = v10_6_profile_reset_audit_trail(db, profile_id)
    data = {"version": "10.6", "mode": "operator-rollback-package", "status": "Ready", "ready": True}
    data["content"] = "# v10.6 Operator Rollback Snapshot Package\n\n" + "\n\n".join(
        [snapshot["content"], audit["content"]]
    )
    return data


def _snapshot_profile_project(db: Session, profile_id: str) -> dict:
    seed = SAMPLE_PROFILE_SEEDS.get(profile_id)
    if not seed:
        return {"ready": False, "status": "Unknown profile", "profile_id": profile_id, "tables": {}}
    project = db.scalars(select(Project).where(Project.name == seed["project"][0])).first()
    if not project:
        return {"ready": False, "status": "Project not built yet", "profile_id": profile_id, "tables": {}}
    tables = {"projects": [_project_row(project)]}
    for table in Base.metadata.sorted_tables:
        if table.name == "projects" or "project_id" not in table.c:
            continue
        rows = db.execute(table.select().where(table.c.project_id == project.id)).mappings().all()
        if rows:
            tables[table.name] = [_clean_row(dict(row)) for row in rows]
    counts = {name: len(rows) for name, rows in tables.items()}
    return {
        "ready": True,
        "status": "Snapshot ready",
        "profile_id": profile_id,
        "project_id": project.id,
        "tables": tables,
        "counts": counts,
    }


def _write_audit(db: Session, profile_id: str, operator_name: str, before: dict, after: dict, result: dict) -> dict:
    event = {
        "profile_id": profile_id,
        "operator_name": operator_name or "unknown",
        "status": result.get("status"),
        "before_digest": _digest(before),
        "after_digest": _digest(after),
        "before_counts": before.get("counts", {}),
        "after_counts": after.get("counts", {}),
        "rollback_snapshot": before,
    }
    db.add(
        ActivityLog(
            project_id=None, action=AUDIT_ACTION, message=json.dumps(event, default=_json_default, sort_keys=True)
        )
    )
    db.commit()
    return {k: event[k] for k in event if k != "rollback_snapshot"}


def _with_v106(result: dict, before: dict | None, audit: dict | None) -> dict:
    result = dict(result)
    result["version"] = "10.6"
    result["mode"] = "profile-reset-execution-with-audit"
    if before:
        result["rollback_snapshot_digest"] = _digest(before)
        result["rollback_snapshot_counts"] = before.get("counts", {})
    if audit:
        result["audit_event"] = audit
    result["content"] = _execute_markdown(result)
    return result


def _decode_event(row: ActivityLog) -> dict:
    data = json.loads(row.message)
    data["audit_id"] = row.id
    data["created_at"] = _json_default(row.created_at)
    return data


def _project_row(project: Project) -> dict:
    return _clean_row(
        {"id": project.id, "name": project.name, "description": project.description, "created_at": project.created_at}
    )


def _clean_row(row: dict) -> dict:
    return {key: _json_default(value) for key, value in row.items()}


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _digest(data: dict) -> str:
    payload = json.dumps(data, default=_json_default, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _snapshot_markdown(data: dict) -> str:
    lines = [
        "# v10.6 Rollback Snapshot Export",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        f"Digest: `{data['snapshot_digest']}`",
        "",
        "## Counts",
    ]
    counts = data["snapshot"].get("counts", {})
    lines.extend(f"- {name}: {count}" for name, count in counts.items())
    return "\n".join(lines).strip() + "\n"


def _audit_markdown(data: dict) -> str:
    lines = ["# v10.6 Profile Reset Audit Trail", "", f"Profile: {data['profile_id']}"]
    if not data["audit_events"]:
        lines.append("No reset audit events recorded yet.")
    for event in data["audit_events"]:
        lines.append(f"- Audit #{event['audit_id']}: {event['status']} by {event['operator_name']}")
    return "\n".join(lines).strip() + "\n"


def _execute_markdown(data: dict) -> str:
    lines = [
        "# v10.6 Profile Reset With Audit",
        "",
        f"Status: {data.get('status')}",
        f"Profile: {data.get('profile_id')}",
    ]
    if data.get("rollback_snapshot_digest"):
        lines.append(f"Rollback snapshot digest: `{data['rollback_snapshot_digest']}`")
    return "\n".join(lines).strip() + "\n"
