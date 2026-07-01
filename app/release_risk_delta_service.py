from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReleaseSignOff
from app.release_snapshot_service import snapshot_from_signoff


def release_risk_delta(db: Session, project_id: int, base_id: int | None = None, target_id: int | None = None) -> dict:
    signoffs = _project_signoffs(db, project_id)
    if len(signoffs) < 2 and not (base_id and target_id):
        return {
            "project_id": project_id,
            "can_compare": False,
            "message": "At least two structured approval snapshots are needed for risk delta analytics.",
            "records_available": [_signoff_summary(row) for row in signoffs],
            "content": "No risk delta available yet. Create at least two final approval records first.\n",
        }
    base = db.get(ReleaseSignOff, base_id) if base_id else signoffs[1]
    target = db.get(ReleaseSignOff, target_id) if target_id else signoffs[0]
    if not base or not target or base.project_id != project_id or target.project_id != project_id:
        return {
            "project_id": project_id,
            "can_compare": False,
            "message": "Selected approval records do not belong to this project.",
            "records_available": [_signoff_summary(row) for row in signoffs],
            "content": "Selected approval records are invalid for this project.\n",
        }
    base_snapshot = snapshot_from_signoff(base)
    target_snapshot = snapshot_from_signoff(target)
    base_rows = _requirement_map(base_snapshot)
    target_rows = _requirement_map(target_snapshot)
    added = [_delta_row(None, target_rows[key]) for key in sorted(set(target_rows) - set(base_rows))]
    removed = [_delta_row(base_rows[key], None) for key in sorted(set(base_rows) - set(target_rows))]
    changed = [_delta_row(base_rows[key], target_rows[key]) for key in sorted(set(base_rows) & set(target_rows))]
    worsened = [row for row in changed if row["risk_delta"] > 0 or row["blocking_risk_delta"] > 0]
    improved = [row for row in changed if row["risk_delta"] < 0 or row["blocking_risk_delta"] < 0]
    stable = [row for row in changed if row["risk_delta"] == 0 and row["blocking_risk_delta"] == 0]
    summary = _summary_delta(base_snapshot, target_snapshot)
    data = {
        "project_id": project_id,
        "can_compare": True,
        "base": _signoff_summary(base),
        "target": _signoff_summary(target),
        "summary": summary,
        "added_requirements": added,
        "removed_requirements": removed,
        "worsened_requirements": worsened,
        "improved_requirements": improved,
        "stable_requirements": stable,
        "action_hints": _action_hints(summary, worsened, added),
        "records_available": [_signoff_summary(row) for row in signoffs],
    }
    data["content"] = risk_delta_markdown(data)
    return data


def risk_delta_markdown(data: dict) -> str:
    if not data.get("can_compare"):
        return data.get("content", "No risk delta available.\n")
    summary = data["summary"]
    lines = [
        "# Release Risk Delta Analytics",
        "",
        f"Base: {data['base']['release_version']} · {data['base']['created_at']}",
        f"Target: {data['target']['release_version']} · {data['target']['created_at']}",
        "",
        "## Summary",
        f"- Total risk delta: {summary['total_risks_delta']:+d}",
        f"- Blocking risk delta: {summary['blocking_risks_delta']:+d}",
        f"- Requirement delta: {summary['requirement_delta']:+d}",
        f"- Done requirement delta: {summary['done_requirements_delta']:+d}",
        "",
        "## Action hints",
    ]
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])] or ["- No urgent delta action detected."])
    lines.extend(["", "## Worsened requirements"])
    lines.extend(_markdown_rows(data.get("worsened_requirements", [])))
    lines.extend(["", "## Improved requirements"])
    lines.extend(_markdown_rows(data.get("improved_requirements", [])))
    lines.extend(["", "## Added requirements"])
    lines.extend(_markdown_rows(data.get("added_requirements", [])))
    lines.extend(["", "## Removed requirements"])
    lines.extend(_markdown_rows(data.get("removed_requirements", [])))
    return "\n".join(lines).strip() + "\n"


def _project_signoffs(db: Session, project_id: int) -> list[ReleaseSignOff]:
    return list(
        db.scalars(
            select(ReleaseSignOff)
            .where(ReleaseSignOff.project_id == project_id)
            .order_by(ReleaseSignOff.created_at.desc())
        ).all()
    )


def _requirement_map(snapshot: dict) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for req in snapshot.get("requirements", []) or []:
        key = (req.get("key") or req.get("requirement_key") or "").strip()
        if key:
            rows[key] = {
                "key": key,
                "title": req.get("title") or req.get("requirement_title") or "",
                "risk_count": int(req.get("risk_count", 0) or 0),
                "blocking_risks": int(req.get("blocking_risks", 0) or 0),
                "is_done": bool(req.get("is_done")),
                "review_complete": bool(req.get("review_complete")),
            }
    return rows


def _delta_row(base: dict | None, target: dict | None) -> dict:
    current = target or base or {}
    base_risk = int((base or {}).get("risk_count", 0) or 0)
    target_risk = int((target or {}).get("risk_count", 0) or 0)
    base_blocking = int((base or {}).get("blocking_risks", 0) or 0)
    target_blocking = int((target or {}).get("blocking_risks", 0) or 0)
    return {
        "requirement_key": current.get("key", ""),
        "requirement_title": current.get("title", ""),
        "base_risk_count": base_risk,
        "target_risk_count": target_risk,
        "risk_delta": target_risk - base_risk,
        "base_blocking_risks": base_blocking,
        "target_blocking_risks": target_blocking,
        "blocking_risk_delta": target_blocking - base_blocking,
        "base_done": bool((base or {}).get("is_done")),
        "target_done": bool((target or {}).get("is_done")),
    }


def _summary_delta(base_snapshot: dict, target_snapshot: dict) -> dict:
    base = base_snapshot.get("summary", {}) or {}
    target = target_snapshot.get("summary", {}) or {}
    base_req = int(base.get("total_requirements", len(base_snapshot.get("requirements", []))) or 0)
    target_req = int(target.get("total_requirements", len(target_snapshot.get("requirements", []))) or 0)
    return {
        "base_total_risks": int(base.get("total_risks", 0) or 0),
        "target_total_risks": int(target.get("total_risks", 0) or 0),
        "total_risks_delta": int(target.get("total_risks", 0) or 0) - int(base.get("total_risks", 0) or 0),
        "base_blocking_risks": int(base.get("blocking_risks", 0) or 0),
        "target_blocking_risks": int(target.get("blocking_risks", 0) or 0),
        "blocking_risks_delta": int(target.get("blocking_risks", 0) or 0) - int(base.get("blocking_risks", 0) or 0),
        "base_requirements": base_req,
        "target_requirements": target_req,
        "requirement_delta": target_req - base_req,
        "base_done_requirements": int(base.get("done_requirements", 0) or 0),
        "target_done_requirements": int(target.get("done_requirements", 0) or 0),
        "done_requirements_delta": int(target.get("done_requirements", 0) or 0)
        - int(base.get("done_requirements", 0) or 0),
    }


def _action_hints(summary: dict, worsened: list[dict], added: list[dict]) -> list[str]:
    hints: list[str] = []
    if summary["blocking_risks_delta"] > 0:
        hints.append("Blocking risk increased. Review worsened requirements before approving the next release.")
    if summary["total_risks_delta"] > 0:
        hints.append(
            "Total risk increased. Add prevention checklist items for repeated or newly introduced risk patterns."
        )
    for row in worsened[:3]:
        hints.append(
            f"Focus {row['requirement_key']}: risk {row['base_risk_count']} → {row['target_risk_count']}, blocking {row['base_blocking_risks']} → {row['target_blocking_risks']}."
        )
    if added:
        hints.append(
            "New requirements appeared since the base snapshot. Confirm each one has task/test coverage and review completion."
        )
    if not hints:
        hints.append(
            "Risk did not worsen between the selected snapshots. Keep the current prevention checklist active."
        )
    return hints


def _signoff_summary(signoff: ReleaseSignOff) -> dict:
    return {
        "id": signoff.id,
        "release_version": signoff.release_version,
        "approved_by": signoff.approved_by,
        "created_at": signoff.created_at.isoformat() if signoff.created_at else None,
        "has_structured_snapshot": bool(signoff.snapshot_json),
    }


def _markdown_rows(rows: list[dict]) -> list[str]:
    if not rows:
        return ["- None"]
    return [
        f"- {row['requirement_key']} — {row['requirement_title']} | risk {row['base_risk_count']} → {row['target_risk_count']} ({row['risk_delta']:+d}) | blocking {row['base_blocking_risks']} → {row['target_blocking_risks']} ({row['blocking_risk_delta']:+d})"
        for row in rows
    ]
