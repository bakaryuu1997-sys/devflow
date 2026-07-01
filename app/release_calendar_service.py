from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem
from app.release_calendar_export import prevention_calendar_markdown, release_readiness_timeline_markdown
from app.release_learning_helpers import DONE_STATUSES


def prevention_calendar_view(db: Session, project_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    project = db.get(Project, project_id)
    rows = [_calendar_row(item, today) for item in _items(db, project_id)]
    open_rows = [row for row in rows if not row["is_done"]]
    scheduled = [row for row in open_rows if row["due_date"]]
    unscheduled = [row for row in open_rows if not row["due_date"]]
    overdue = [row for row in scheduled if row["is_overdue"]]
    calendar = _calendar_days(scheduled)
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "today": today.isoformat(),
        "total_items": len(rows),
        "open_items": len(open_rows),
        "scheduled_items": len(scheduled),
        "unscheduled_items": len(unscheduled),
        "overdue_items": len(overdue),
        "calendar": calendar,
        "overdue": overdue,
        "unscheduled": unscheduled,
        "action_hints": _calendar_hints(overdue, unscheduled, scheduled),
    }
    data["content"] = prevention_calendar_markdown(data)
    return data


def release_readiness_timeline(db: Session, project_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    project = db.get(Project, project_id)
    rows = [_calendar_row(item, today) for item in _items(db, project_id)]
    open_rows = [row for row in rows if not row["is_done"]]
    checkpoints = [_timeline_checkpoint(label, days, open_rows, today) for label, days in _CHECKPOINTS]
    overall = _overall_status(checkpoints, open_rows)
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "today": today.isoformat(),
        "total_items": len(rows),
        "open_items": len(open_rows),
        "overall_status": overall,
        "checkpoints": checkpoints,
        "action_hints": _timeline_hints(checkpoints, open_rows),
    }
    data["content"] = release_readiness_timeline_markdown(data)
    return data


_CHECKPOINTS = [("Today", 0), ("7 days", 7), ("14 days", 14), ("30 days", 30)]


def _items(db: Session, project_id: int) -> list[ReleaseLearningItem]:
    return list(
        db.scalars(
            select(ReleaseLearningItem)
            .where(ReleaseLearningItem.project_id == project_id)
            .order_by(ReleaseLearningItem.created_at.asc(), ReleaseLearningItem.id.asc())
        ).all()
    )


def _calendar_row(item: ReleaseLearningItem, today: date) -> dict:
    due = getattr(item, "due_date", "") or ""
    due_day = _parse_date(due)
    is_done = item.status in DONE_STATUSES
    return {
        "id": item.id,
        "title": item.title,
        "source": item.source,
        "prevention_action": item.prevention_action,
        "status": item.status,
        "owner": getattr(item, "owner", "") or "",
        "due_date": due,
        "is_done": is_done,
        "is_overdue": bool(not is_done and due_day and due_day < today),
        "days_until_due": (due_day - today).days if due_day else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _calendar_days(scheduled: list[dict]) -> list[dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in scheduled:
        buckets[row["due_date"][:10]].append(row)
    result = []
    for due_day in sorted(buckets):
        items = sorted(buckets[due_day], key=lambda row: (row["owner"] or "~", row["id"]))
        result.append(
            {"date": due_day, "bucket": _bucket(items[0]["days_until_due"]), "count": len(items), "items": items}
        )
    return result


def _timeline_checkpoint(label: str, days: int, open_rows: list[dict], today: date) -> dict:
    checkpoint = today + timedelta(days=days)
    unscheduled = [row for row in open_rows if not row["due_date"]]
    overdue = [row for row in open_rows if _due(row) and _due(row) < checkpoint]
    planned_closed = [row for row in open_rows if _due(row) and _due(row) <= checkpoint]
    remaining = max(0, len(open_rows) - len(planned_closed))
    score = max(0, 100 - remaining * 15 - len(overdue) * 10 - len(unscheduled) * 8)
    return {
        "label": label,
        "date": checkpoint.isoformat(),
        "readiness_score": score,
        "status": _checkpoint_status(score, overdue, unscheduled),
        "planned_closed_by_checkpoint": len(planned_closed),
        "remaining_open_items": remaining,
        "overdue_by_checkpoint": len(overdue),
        "unscheduled_open_items": len(unscheduled),
        "at_risk_items": overdue[:5] + unscheduled[:5],
    }


def _due(row: dict) -> date | None:
    return _parse_date(row.get("due_date", ""))


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _bucket(days: int | None) -> str:
    if days is None:
        return "Unscheduled"
    if days < 0:
        return "Overdue"
    if days <= 7:
        return "This week"
    if days <= 14:
        return "Next 14 days"
    if days <= 30:
        return "Next 30 days"
    return "Later"


def _checkpoint_status(score: int, overdue: list[dict], unscheduled: list[dict]) -> str:
    if overdue:
        return "At Risk"
    if unscheduled or score < 80:
        return "Needs Planning"
    return "On Track"


def _overall_status(checkpoints: list[dict], open_rows: list[dict]) -> str:
    if not open_rows:
        return "Ready"
    if any(row["status"] == "At Risk" for row in checkpoints):
        return "At Risk"
    if any(row["status"] == "Needs Planning" for row in checkpoints):
        return "Needs Planning"
    return "On Track"


def _calendar_hints(overdue: list[dict], unscheduled: list[dict], scheduled: list[dict]) -> list[str]:
    hints = []
    if overdue:
        hints.append(f"Re-plan or close {len(overdue)} overdue prevention item(s).")
    if unscheduled:
        hints.append(f"Add due dates for {len(unscheduled)} unscheduled prevention item(s).")
    if scheduled and not hints:
        hints.append("Calendar is planned; review due-soon items during release planning.")
    if not scheduled and not unscheduled:
        hints.append("No open prevention work remains; keep this calendar ready for the next cycle.")
    return hints


def _timeline_hints(checkpoints: list[dict], open_rows: list[dict]) -> list[str]:
    if not open_rows:
        return ["All prevention work is closed; release readiness timeline is clear."]
    hints = [f"{row['label']}: {row['status']} with score {row['readiness_score']}." for row in checkpoints]
    if checkpoints[-1]["remaining_open_items"]:
        hints.append("Some prevention work remains beyond 30 days; review scope before final sign-off.")
    return hints
