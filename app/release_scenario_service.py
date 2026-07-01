from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem, ScopeDecisionAudit
from app.release_learning_helpers import DONE_STATUSES
from app.release_learning_service import _learning_item_dict
from app.release_scenario_export import scenario_planning_markdown, scope_adjustment_markdown

SCOPED_OUT_STATUSES = {"Deferred", "Out of Scope"}


def release_readiness_scenarios(db: Session, project_id: int, target_days: int = 14, today: date | None = None) -> dict:
    today = today or date.today()
    target_days = max(1, min(int(target_days or 14), 90))
    project = db.get(Project, project_id)
    rows = [_row(item, today) for item in _items(db, project_id)]
    active = [row for row in rows if row["is_active_scope"]]
    scenarios = [
        _scenario("Baseline", "Current release prevention scope.", active, active, target_days),
        _scenario(
            "Complete overdue first",
            "Assume overdue items are closed before release review.",
            active,
            [r for r in active if not r["is_overdue"]],
            target_days,
        ),
        _scenario(
            "Defer unscheduled",
            "Move unscheduled items out of current release scope.",
            active,
            [r for r in active if r["due_date"]],
            target_days,
        ),
        _scenario(
            "Fast-track target window",
            f"Assume items due within {target_days} day(s) are completed.",
            active,
            [r for r in active if not _within_target(r, target_days)],
            target_days,
        ),
    ]
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "today": today.isoformat(),
        "target_days": target_days,
        "total_items": len(rows),
        "active_scope_items": len(active),
        "scoped_out_items": len([row for row in rows if row["is_scoped_out"]]),
        "scenarios": scenarios,
        "action_hints": _hints(scenarios),
    }
    data["content"] = scenario_planning_markdown(data)
    return data


def adjust_prevention_scope(
    db: Session, item_id: int, status: str, owner: str = "", due_date: str = "", reason: str = ""
) -> dict | None:
    item = db.get(ReleaseLearningItem, item_id)
    if not item:
        return None
    old_status = item.status or ""
    new_status = _normalize_status(status)
    item.status = new_status
    if owner:
        item.owner = owner.strip()
    if due_date:
        item.due_date = due_date.strip()
    clean_reason = reason.strip()
    if clean_reason:
        item.prevention_action = _append_scope_note(item.prevention_action, clean_reason)
    db.add(
        ScopeDecisionAudit(
            project_id=item.project_id,
            learning_item_id=item.id,
            old_status=old_status,
            new_status=new_status,
            reason=clean_reason or "Scope adjusted without reason.",
        )
    )
    db.commit()
    db.refresh(item)
    data = {
        "updated": True,
        "message": "Prevention scope adjusted.",
        "reason": clean_reason,
        "item": _learning_item_dict(item),
    }
    data["content"] = scope_adjustment_markdown(data)
    return data


def scope_decision_audit_trail(db: Session, project_id: int, limit: int = 50) -> dict:
    project = db.get(Project, project_id)
    audits = db.scalars(
        select(ScopeDecisionAudit)
        .where(ScopeDecisionAudit.project_id == project_id)
        .order_by(ScopeDecisionAudit.created_at.desc())
        .limit(max(1, min(limit, 100)))
    ).all()
    rows = [_audit_row(db, audit) for audit in audits]
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "audit_count": len(rows),
        "decisions": rows,
    }
    data["content"] = _audit_markdown(data)
    return data


def _items(db: Session, project_id: int) -> list[ReleaseLearningItem]:
    return list(
        db.scalars(
            select(ReleaseLearningItem)
            .where(ReleaseLearningItem.project_id == project_id)
            .order_by(ReleaseLearningItem.id.asc())
        ).all()
    )


def _row(item: ReleaseLearningItem, today: date) -> dict:
    due_day = _parse_date(getattr(item, "due_date", "") or "")
    status = item.status or "Open"
    is_done = status in DONE_STATUSES
    is_scoped_out = status in SCOPED_OUT_STATUSES
    return {
        **_learning_item_dict(item),
        "is_done": is_done,
        "is_scoped_out": is_scoped_out,
        "is_active_scope": not is_done and not is_scoped_out,
        "is_overdue": bool(due_day and due_day < today and not is_done),
        "days_until_due": (due_day - today).days if due_day else None,
        "is_due_within_target": False,
    }


def _scenario(name: str, note: str, baseline: list[dict], scoped: list[dict], target_days: int) -> dict:
    scoped_ids = {row["id"] for row in scoped}
    overdue = [row for row in scoped if row["is_overdue"]]
    unscheduled = [row for row in scoped if not row["due_date"]]
    due_window = [row for row in scoped if row["days_until_due"] is not None and row["days_until_due"] <= target_days]
    score = max(0, 100 - len(scoped) * 8 - len(overdue) * 12 - len(unscheduled) * 8)
    return {
        "name": name,
        "note": note,
        "status": _status(score, overdue, unscheduled),
        "readiness_score": score,
        "active_scope_items": len(scoped),
        "overdue_items": len(overdue),
        "unscheduled_items": len(unscheduled),
        "due_within_target_items": len(due_window),
        "scope_adjustment": len(baseline) - len(scoped),
        "items_in_scope": scoped[:10],
        "items_out_by_scenario": [row for row in baseline if row["id"] not in scoped_ids][:10],
    }


def _within_target(row: dict, target_days: int) -> bool:
    days = row.get("days_until_due")
    return days is not None and days <= target_days


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _status(score: int, overdue: list[dict], unscheduled: list[dict]) -> str:
    if overdue:
        return "At Risk"
    if unscheduled or score < 80:
        return "Needs Scope Decision"
    return "Ready Candidate"


def _hints(scenarios: list[dict]) -> list[str]:
    baseline = scenarios[0]
    best = max(scenarios, key=lambda row: row["readiness_score"])
    hints = [f"Baseline is {baseline['status']} with score {baseline['readiness_score']}/100."]
    if best["name"] != "Baseline":
        hints.append(f"Best scenario is '{best['name']}' with score {best['readiness_score']}/100.")
    if baseline["unscheduled_items"]:
        hints.append("Decide whether unscheduled prevention items are in scope for this release.")
    if baseline["overdue_items"]:
        hints.append("Close, re-plan, or explicitly defer overdue prevention items before release review.")
    return hints


def _normalize_status(status: str) -> str:
    allowed = {"Open", "Planned", "Deferred", "Out of Scope", "Prevented", "Done", "Escalated"}
    clean = (status or "Open").strip()
    return clean if clean in allowed else "Open"


def _append_scope_note(action: str, reason: str) -> str:
    note = f"Scope note: {reason}"
    return action if note in action else f"{action.strip()}\n{note}".strip()


def _audit_row(db: Session, audit: ScopeDecisionAudit) -> dict:
    item = db.get(ReleaseLearningItem, audit.learning_item_id)
    return {
        "id": audit.id,
        "learning_item_id": audit.learning_item_id,
        "item_title": item.title if item else "Deleted prevention item",
        "old_status": audit.old_status,
        "new_status": audit.new_status,
        "reason": audit.reason,
        "created_at": audit.created_at.isoformat() if audit.created_at else None,
    }


def _audit_markdown(data: dict) -> str:
    lines = [
        "# Scope Decision Audit Trail",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        "",
        "## Decisions",
    ]
    if not data["decisions"]:
        lines.append("- No scope decisions recorded yet.")
    for row in data["decisions"]:
        lines.append(
            f"- #{row['id']} item #{row['learning_item_id']} {row['item_title']}: {row['old_status']} → {row['new_status']} — {row['reason']}"
        )
    return "\n".join(lines).strip() + "\n"
