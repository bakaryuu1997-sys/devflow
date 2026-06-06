from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem
from app.release_learning_helpers import DONE_STATUSES
from app.release_prevention_analytics_export import owner_workload_markdown, prevention_burndown_markdown

def prevention_burndown_analytics(db: Session, project_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    project = db.get(Project, project_id)
    rows = [_analytics_row(item, today) for item in _items(db, project_id)]
    open_rows = [row for row in rows if not row["is_done"]]
    done_rows = [row for row in rows if row["is_done"]]
    overdue = [row for row in open_rows if row["is_overdue"]]
    due_soon = [row for row in open_rows if row["is_due_soon"]]
    projection = _burndown_projection(open_rows, today)
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "total_items": len(rows),
        "open_items": len(open_rows),
        "done_items": len(done_rows),
        "overdue_items": len(overdue),
        "due_soon_items": len(due_soon),
        "completion_rate": _pct(len(done_rows), len(rows)),
        "status_counts": _count_by(rows, "status"),
        "burndown_projection": projection,
        "at_risk_items": overdue + due_soon,
        "action_hints": _burndown_hints(open_rows, overdue, due_soon, projection),
    }
    data["content"] = prevention_burndown_markdown(data)
    return data

def owner_workload_balance(db: Session, project_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    project = db.get(Project, project_id)
    rows = [_analytics_row(item, today) for item in _items(db, project_id)]
    owner_rows = _owner_rows(rows)
    open_counts = [row["open_items"] for row in owner_rows if row["owner"] != "Unassigned"]
    avg_open = round(sum(open_counts) / len(open_counts), 2) if open_counts else 0
    overloaded = [row for row in owner_rows if row["owner"] != "Unassigned" and row["workload_score"] >= max(8, avg_open * 4)]
    unassigned = next((row for row in owner_rows if row["owner"] == "Unassigned"), None)
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "owner_count": len([row for row in owner_rows if row["owner"] != "Unassigned"]),
        "average_open_items_per_owner": avg_open,
        "unassigned_open_items": unassigned["open_items"] if unassigned else 0,
        "overloaded_owner_count": len(overloaded),
        "owners": owner_rows,
        "action_hints": _owner_hints(owner_rows, overloaded, unassigned),
    }
    data["content"] = owner_workload_markdown(data)
    return data
def _items(db: Session, project_id: int) -> list[ReleaseLearningItem]:
    return list(db.scalars(
        select(ReleaseLearningItem)
        .where(ReleaseLearningItem.project_id == project_id)
        .order_by(ReleaseLearningItem.created_at.asc(), ReleaseLearningItem.id.asc())
    ).all())
def _analytics_row(item: ReleaseLearningItem, today: date) -> dict:
    due = getattr(item, "due_date", "") or ""
    due_day = _parse_date(due)
    is_done = item.status in DONE_STATUSES
    owner = getattr(item, "owner", "") or ""
    return {
        "id": item.id,
        "project_id": item.project_id,
        "source": item.source,
        "title": item.title,
        "prevention_action": item.prevention_action,
        "status": item.status,
        "owner": owner,
        "due_date": due,
        "is_done": is_done,
        "is_overdue": bool(not is_done and due_day and due_day < today),
        "is_due_soon": bool(not is_done and due_day and today <= due_day <= today + timedelta(days=7)),
        "days_until_due": _days_until_due(due_day, today) if due_day else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }
def _burndown_projection(open_rows: list[dict], today: date) -> list[dict]:
    checkpoints = [("today", 0), ("7_days", 7), ("14_days", 14), ("30_days", 30)]
    projection = []
    for label, days in checkpoints:
        checkpoint = today + timedelta(days=days)
        planned_done = 0
        missing_due = 0
        for row in open_rows:
            due_day = _parse_date(row.get("due_date", ""))
            if due_day and due_day <= checkpoint:
                planned_done += 1
            if not due_day:
                missing_due += 1
        remaining = max(0, len(open_rows) - planned_done)
        projection.append({
            "checkpoint": label,
            "date": checkpoint.isoformat(),
            "planned_closed_by_checkpoint": planned_done,
            "remaining_open_items": remaining,
            "missing_due_date_items": missing_due,
        })
    return projection
def _owner_rows(rows: list[dict]) -> list[dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[row.get("owner") or "Unassigned"].append(row)
    owner_rows = []
    for owner, items in buckets.items():
        open_items = [row for row in items if not row["is_done"]]
        overdue = [row for row in open_items if row["is_overdue"]]
        due_soon = [row for row in open_items if row["is_due_soon"]]
        escalated = [row for row in open_items if row["status"] == "Escalated"]
        score = len(open_items) * 3 + len(overdue) * 5 + len(due_soon) * 2 + len(escalated) * 4
        owner_rows.append({
            "owner": owner,
            "total_items": len(items),
            "open_items": len(open_items),
            "done_items": len(items) - len(open_items),
            "overdue_items": len(overdue),
            "due_soon_items": len(due_soon),
            "escalated_items": len(escalated),
            "workload_score": score,
            "status": _owner_status(owner, open_items, overdue, due_soon, escalated, score),
            "items": open_items,
        })
    return sorted(owner_rows, key=lambda row: (row["owner"] == "Unassigned", -row["workload_score"], row["owner"]))
def _owner_status(owner: str, open_items: list[dict], overdue: list[dict], due_soon: list[dict], escalated: list[dict], score: int) -> str:
    if owner == "Unassigned" and open_items:
        return "Needs Owner"
    if overdue or escalated or score >= 12:
        return "Overloaded"
    if due_soon or score >= 6:
        return "Watch"
    return "Balanced"
def _count_by(rows: list[dict], field: str) -> dict:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(field) or "Unknown"
        counts[key] = counts.get(key, 0) + 1
    return counts
def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None
def _days_until_due(due_day: date | None, today: date) -> int | None:
    return (due_day - today).days if due_day else None
def _pct(part: int, total: int) -> int:
    return int(round((part / total) * 100)) if total else 100
def _burndown_hints(open_rows: list[dict], overdue: list[dict], due_soon: list[dict], projection: list[dict]) -> list[str]:
    hints = []
    missing_due = projection[-1]["missing_due_date_items"] if projection else 0
    if overdue:
        hints.append(f"Close or re-plan {len(overdue)} overdue prevention item(s) before the next release review.")
    if due_soon:
        hints.append(f"Verify progress for {len(due_soon)} item(s) due within 7 days.")
    if missing_due:
        hints.append(f"Set due dates for {missing_due} open prevention item(s) so burndown becomes trackable.")
    if open_rows and not hints:
        hints.append("Track planned closure against due dates and mark items Prevented as soon as risk is controlled.")
    if not open_rows:
        hints.append("All prevention work is closed; keep the checklist ready for the next release cycle.")
    return hints
def _owner_hints(owner_rows: list[dict], overloaded: list[dict], unassigned: dict | None) -> list[str]:
    hints = []
    if unassigned and unassigned["open_items"]:
        hints.append(f"Assign owner for {unassigned['open_items']} open prevention item(s).")
    if overloaded:
        names = ", ".join(row["owner"] for row in overloaded[:3])
        hints.append(f"Rebalance overloaded owner(s): {names}.")
    watch = [row for row in owner_rows if row["status"] == "Watch"]
    if watch:
        hints.append(f"Check near-term workload for {len(watch)} owner(s) marked Watch.")
    if not hints:
        hints.append("Owner workload is balanced for the current prevention backlog.")
    return hints
