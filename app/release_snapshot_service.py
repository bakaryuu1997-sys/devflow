from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReleaseSignOff


def build_structured_snapshot(raw: dict, approved_by: str = "", approval_note: str = "") -> dict:
    completion = raw.get("completion", {}) or {}
    risk = raw.get("risk_dashboard", {}) or {}
    risk_index = _risk_row_index(risk)
    requirements = [
        _requirement_snapshot(row, risk_index.get(row.get("requirement_key") or row.get("key")))
        for row in completion.get("requirements", [])
    ]
    return {
        "schema_version": "7.0",
        "risk_event_schema_version": "7.2",
        "project": {
            "id": raw.get("project_id"),
            "name": raw.get("project_name", "Unknown project"),
        },
        "release": {
            "id": raw.get("release_id"),
            "version": raw.get("release_version", "unassigned"),
        },
        "approval": {
            "approved_by": (approved_by or "Release owner").strip() or "Release owner",
            "approval_note": (approval_note or "").strip(),
            "decision": "APPROVED" if raw.get("ready_for_signoff") else "WAIT",
            "ready_for_signoff": bool(raw.get("ready_for_signoff")),
        },
        "summary": {
            "generated_at": raw.get("generated_at"),
            "reviewed_requirements": completion.get("reviewed_requirements", 0),
            "done_requirements": completion.get("done_requirements", 0),
            "total_requirements": completion.get("total_requirements", 0),
            "blocking_requirements": completion.get("blocking_requirements", 0),
            "total_risks": risk.get("total_risks", 0),
            "blocking_risks": risk.get("blocking_risks", 0),
            "release_status": risk.get("release_status", "Unknown"),
        },
        "requirements": requirements,
        "signoff_blockers": list(raw.get("signoff_blockers", []) or []),
        "top_actions": list(risk.get("top_actions", []) or []),
    }


def attach_structured_snapshot(raw: dict) -> dict:
    data = dict(raw)
    data["structured_snapshot"] = build_structured_snapshot(raw)
    return data


def snapshot_to_json(snapshot: dict) -> str:
    return json.dumps(snapshot, ensure_ascii=False, sort_keys=True)


def snapshot_from_signoff(signoff: ReleaseSignOff) -> dict:
    if signoff.snapshot_json:
        try:
            data = json.loads(signoff.snapshot_json)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return snapshot_from_legacy_markdown(signoff)


def snapshot_from_legacy_markdown(signoff: ReleaseSignOff) -> dict:
    from app.release_history_service import legacy_approval_rows

    rows = [
        {"key": key, "title": title, "is_done": None, "review_complete": None, "blocking_risks": None}
        for key, title in legacy_approval_rows(signoff.snapshot).items()
    ]
    return {
        "schema_version": "legacy-markdown",
        "project": {"id": signoff.project_id, "name": "Unknown project"},
        "release": {"id": signoff.release_id, "version": signoff.release_version},
        "approval": {
            "approved_by": signoff.approved_by,
            "approval_note": signoff.approval_note,
            "decision": "APPROVED",
            "ready_for_signoff": True,
        },
        "summary": {},
        "requirements": rows,
        "signoff_blockers": [],
        "top_actions": [],
    }


def release_snapshot_analytics(db: Session, project_id: int) -> dict:
    signoffs = list(db.scalars(
        select(ReleaseSignOff).where(ReleaseSignOff.project_id == project_id).order_by(ReleaseSignOff.created_at.desc())
    ).all())
    snapshots = [snapshot_from_signoff(row) for row in signoffs]
    requirement_keys = {req.get("key") for snap in snapshots for req in snap.get("requirements", []) if req.get("key")}
    blocking_counts = [int((snap.get("summary") or {}).get("blocking_risks", 0) or 0) for snap in snapshots]
    return {
        "project_id": project_id,
        "snapshot_count": len(snapshots),
        "structured_snapshot_count": sum(1 for row in signoffs if bool(row.snapshot_json)),
        "legacy_snapshot_count": sum(1 for row in signoffs if not bool(row.snapshot_json)),
        "requirement_count_seen": len(requirement_keys),
        "latest_release_version": snapshots[0].get("release", {}).get("version") if snapshots else None,
        "latest_decision": snapshots[0].get("approval", {}).get("decision") if snapshots else None,
        "max_blocking_risks_at_signoff": max(blocking_counts) if blocking_counts else 0,
        "trend_rows": [_trend_row(row, snap) for row, snap in zip(signoffs, snapshots)],
    }


def _requirement_snapshot(row: dict[str, Any], risk_row: dict | None = None) -> dict:
    risk_row = risk_row or {}
    risks = list(risk_row.get("risks", []) or [])
    return {
        "id": row.get("requirement_id") or row.get("id"),
        "key": row.get("requirement_key") or row.get("key"),
        "title": row.get("requirement_title") or row.get("title"),
        "priority": row.get("priority"),
        "status": row.get("status"),
        "is_done": bool(row.get("is_done")),
        "review_complete": bool(row.get("review_complete")),
        "blocking_risks": int(risk_row.get("blocking_risks", row.get("blocking_risks", 0)) or 0),
        "risk_count": int(risk_row.get("risk_count", row.get("risk_count", len(risks))) or 0),
        "highest_severity": risk_row.get("highest_severity", "Low"),
        "risk_events": [_risk_event_snapshot(risk) for risk in risks],
        "fix_hints": list(risk_row.get("fix_hints", []) or []),
    }


def _risk_row_index(risk_dashboard: dict) -> dict[str, dict]:
    rows = {}
    for row in risk_dashboard.get("requirements", []) or []:
        key = (row.get("requirement_key") or row.get("key") or "").strip()
        if key:
            rows[key] = row
    return rows


def _risk_event_snapshot(risk: dict) -> dict:
    return {
        "rule_id": risk.get("rule_id", "unknown"),
        "title": risk.get("title", "Untitled risk"),
        "message": risk.get("message", ""),
        "severity": risk.get("severity", "Low"),
        "blocking": bool(risk.get("blocking")),
    }


def _trend_row(signoff: ReleaseSignOff, snap: dict) -> dict:
    summary = snap.get("summary", {}) or {}
    return {
        "signoff_id": signoff.id,
        "release_version": snap.get("release", {}).get("version", signoff.release_version),
        "created_at": signoff.created_at.isoformat() if signoff.created_at else None,
        "requirements": summary.get("total_requirements", len(snap.get("requirements", []))),
        "done_requirements": summary.get("done_requirements", 0),
        "blocking_risks": summary.get("blocking_risks", 0),
        "risk_events": sum(len(req.get("risk_events", []) or []) for req in snap.get("requirements", []) or []),
        "schema_version": snap.get("schema_version", "unknown"),
        "risk_event_schema_version": snap.get("risk_event_schema_version"),
    }
