from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem
from app.release_learning_helpers import DONE_STATUSES


def next_release_readiness(db: Session, project_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    project = db.get(Project, project_id)
    items = list(
        db.scalars(
            select(ReleaseLearningItem)
            .where(ReleaseLearningItem.project_id == project_id)
            .order_by(ReleaseLearningItem.created_at.desc())
        ).all()
    )
    rows = [_planning_row(item, today) for item in items]
    open_rows = [row for row in rows if row["status"] not in DONE_STATUSES]
    planned_rows = [row for row in open_rows if row["owner"] and row["due_date"]]
    unassigned = [row for row in open_rows if not row["owner"]]
    missing_due = [row for row in open_rows if not row["due_date"]]
    overdue = [row for row in open_rows if row["is_overdue"]]
    due_soon = [row for row in open_rows if row["is_due_soon"]]
    score = _score(len(open_rows), len(unassigned), len(missing_due), len(overdue))
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "score": score,
        "status": _status(score, open_rows, overdue),
        "total_items": len(rows),
        "open_items": len(open_rows),
        "planned_open_items": len(planned_rows),
        "unassigned_items": len(unassigned),
        "missing_due_date_items": len(missing_due),
        "overdue_items": len(overdue),
        "due_soon_items": len(due_soon),
        "items": rows,
        "action_hints": _action_hints(open_rows, unassigned, missing_due, overdue, due_soon),
    }
    data["content"] = next_release_readiness_markdown(data)
    return data


def next_release_readiness_markdown(data: dict) -> str:
    lines = [
        "# Next Release Readiness",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Status: {data['status']}",
        f"Score: {data['score']}/100",
        "",
        "## Summary",
        f"- Open prevention items: {data['open_items']}",
        f"- Planned open items: {data['planned_open_items']}",
        f"- Unassigned items: {data['unassigned_items']}",
        f"- Missing due dates: {data['missing_due_date_items']}",
        f"- Overdue items: {data['overdue_items']}",
        "",
        "## Action hints",
    ]
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])])
    lines.extend(["", "## Prevention planning"])
    if not data.get("items"):
        lines.append("- No saved prevention items yet.")
    for item in data.get("items", []):
        checked = "x" if item["status"] in DONE_STATUSES else " "
        lines.append(
            f"- [{checked}] #{item['id']} {item['title']} | owner={item['owner'] or 'Unassigned'} | "
            f"due={item['due_date'] or 'No due date'} | status={item['status']}"
        )
    return "\n".join(lines).strip() + "\n"


def _planning_row(item: ReleaseLearningItem, today: date) -> dict:
    due = getattr(item, "due_date", "") or ""
    due_day = _parse_date(due)
    is_open = item.status not in DONE_STATUSES
    return {
        "id": item.id,
        "project_id": item.project_id,
        "source": item.source,
        "title": item.title,
        "prevention_action": item.prevention_action,
        "status": item.status,
        "owner": getattr(item, "owner", "") or "",
        "due_date": due,
        "is_overdue": bool(is_open and due_day and due_day < today),
        "is_due_soon": bool(is_open and due_day and today <= due_day <= today + timedelta(days=7)),
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _score(open_count: int, unassigned_count: int, missing_due_count: int, overdue_count: int) -> int:
    penalty = open_count * 8 + unassigned_count * 12 + missing_due_count * 12 + overdue_count * 25
    return max(0, min(100, 100 - penalty))


def _status(score: int, open_rows: list[dict], overdue_rows: list[dict]) -> str:
    if not open_rows:
        return "Ready"
    if overdue_rows:
        return "At Risk"
    if score >= 70:
        return "Planning Needed"
    return "At Risk"


def _action_hints(
    open_rows: list[dict], unassigned: list[dict], missing_due: list[dict], overdue: list[dict], due_soon: list[dict]
) -> list[str]:
    hints = []
    if overdue:
        hints.append(f"Fix or re-plan {len(overdue)} overdue prevention item(s) before release review starts.")
    if unassigned:
        hints.append(f"Assign an owner for {len(unassigned)} open prevention item(s).")
    if missing_due:
        hints.append(f"Set due dates for {len(missing_due)} open prevention item(s).")
    if due_soon:
        hints.append(f"Review {len(due_soon)} prevention item(s) due within 7 days.")
    if open_rows and not hints:
        hints.append("Close or mark prevention items as Prevented once the recurring risk is controlled.")
    if not open_rows:
        hints.append("No open prevention item remains; the next release is ready from the prevention-planning view.")
    return hints
