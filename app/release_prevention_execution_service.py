from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem
from app.release_learning_helpers import DONE_STATUSES
from app.release_prevention_execution_export import (
    overdue_risk_escalations_markdown,
    prevention_execution_board_markdown,
)

ESCALATED_STATUS = "Escalated"


def prevention_execution_board(db: Session, project_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    project = db.get(Project, project_id)
    items = list(db.scalars(
        select(ReleaseLearningItem)
        .where(ReleaseLearningItem.project_id == project_id)
        .order_by(ReleaseLearningItem.created_at.desc())
    ).all())
    rows = [_execution_row(item, today) for item in items]
    open_rows = [row for row in rows if not row["is_done"]]
    escalated_rows = [row for row in open_rows if row["status"] == ESCALATED_STATUS]
    overdue_rows = [row for row in open_rows if row["is_overdue"]]
    due_soon_rows = [row for row in open_rows if row["is_due_soon"]]
    unplanned_rows = [row for row in open_rows if row["lane"] == "Unplanned"]
    lanes = {
        "Escalated": [row for row in open_rows if row["lane"] == "Escalated"],
        "Overdue": [row for row in open_rows if row["lane"] == "Overdue"],
        "Due Soon": [row for row in open_rows if row["lane"] == "Due Soon"],
        "Planned": [row for row in open_rows if row["lane"] == "Planned"],
        "Unplanned": unplanned_rows,
        "Done": [row for row in rows if row["is_done"]],
    }
    escalations = [_escalation(row) for row in overdue_rows + [r for r in escalated_rows if not r["is_overdue"]]]
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "total_items": len(rows),
        "open_items": len(open_rows),
        "planned_items": len([row for row in open_rows if row["owner"] and row["due_date"]]),
        "unplanned_items": len(unplanned_rows),
        "due_soon_items": len(due_soon_rows),
        "overdue_items": len(overdue_rows),
        "escalated_items": len(escalated_rows),
        "done_items": len(lanes["Done"]),
        "lanes": lanes,
        "items": rows,
        "escalations": escalations,
        "action_hints": _action_hints(open_rows, unplanned_rows, due_soon_rows, overdue_rows, escalated_rows),
    }
    data["content"] = prevention_execution_board_markdown(data)
    return data


def escalate_learning_item(db: Session, item_id: int, reason: str = "") -> dict | None:
    item = db.get(ReleaseLearningItem, item_id)
    if not item:
        return None
    if item.status in DONE_STATUSES:
        return {
            "message": "Done prevention items are not escalated.",
            "item": _learning_item_dict(item),
            "changed": False,
        }
    item.status = ESCALATED_STATUS
    if reason:
        current = item.prevention_action or ""
        marker = f"Escalation note: {reason.strip()}"
        if marker not in current:
            item.prevention_action = (current + "\n" + marker).strip()
    db.commit()
    db.refresh(item)
    return {
        "message": "Prevention item escalated.",
        "item": _learning_item_dict(item),
        "changed": True,
    }


def overdue_risk_escalations(db: Session, project_id: int, today: date | None = None) -> dict:
    board = prevention_execution_board(db, project_id, today)
    data = {
        "project_id": board["project_id"],
        "project_name": board["project_name"],
        "overdue_items": board["overdue_items"],
        "escalated_items": board["escalated_items"],
        "escalations": board["escalations"],
        "action_hints": board["action_hints"],
    }
    data["content"] = overdue_risk_escalations_markdown(data)
    return data

def _execution_row(item: ReleaseLearningItem, today: date) -> dict:
    due = getattr(item, "due_date", "") or ""
    due_day = _parse_date(due)
    is_done = item.status in DONE_STATUSES
    is_overdue = bool(not is_done and due_day and due_day < today)
    is_due_soon = bool(not is_done and due_day and today <= due_day <= today + timedelta(days=7))
    owner = getattr(item, "owner", "") or ""
    row = {
        "id": item.id,
        "project_id": item.project_id,
        "source": item.source,
        "title": item.title,
        "prevention_action": item.prevention_action,
        "status": item.status,
        "owner": owner,
        "due_date": due,
        "is_done": is_done,
        "is_overdue": is_overdue,
        "is_due_soon": is_due_soon,
        "days_overdue": _days_overdue(due_day, today) if is_overdue else 0,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }
    row["lane"] = _lane(row)
    return row


def _lane(row: dict) -> str:
    if row["is_done"]:
        return "Done"
    if row["status"] == ESCALATED_STATUS:
        return "Escalated"
    if row["is_overdue"]:
        return "Overdue"
    if row["is_due_soon"]:
        return "Due Soon"
    if row["owner"] and row["due_date"]:
        return "Planned"
    return "Unplanned"


def _escalation(row: dict) -> dict:
    days = row.get("days_overdue", 0)
    level = "Critical" if days >= 14 else ("High" if days >= 7 else "Medium")
    if row["status"] == ESCALATED_STATUS and not row["is_overdue"]:
        level = "Medium"
    return {
        "id": row["id"],
        "title": row["title"],
        "owner": row["owner"],
        "due_date": row["due_date"],
        "status": row["status"],
        "days_overdue": days,
        "level": level,
        "message": _escalation_message(row, days),
    }


def _escalation_message(row: dict, days: int) -> str:
    if days > 0:
        return f"Prevention item is {days} day(s) overdue and can let recurring release risk return."
    return "Prevention item has been escalated and needs owner follow-up before release planning continues."


def _action_hints(open_rows: list[dict], unplanned: list[dict], due_soon: list[dict], overdue: list[dict], escalated: list[dict]) -> list[str]:
    hints = []
    if overdue:
        hints.append(f"Escalate or re-plan {len(overdue)} overdue prevention item(s) today.")
    if escalated:
        hints.append(f"Review {len(escalated)} escalated prevention item(s) with the release owner.")
    if unplanned:
        hints.append(f"Assign owner and due date for {len(unplanned)} unplanned prevention item(s).")
    if due_soon:
        hints.append(f"Check progress on {len(due_soon)} item(s) due within 7 days.")
    if open_rows and not hints:
        hints.append("Keep executing planned prevention items and mark them Prevented once risk is controlled.")
    if not open_rows:
        hints.append("All prevention items are closed; no execution escalation is currently needed.")
    return hints


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _days_overdue(due_day: date | None, today: date) -> int:
    return max(0, (today - due_day).days) if due_day else 0


def _learning_item_dict(item: ReleaseLearningItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "source": item.source,
        "title": item.title,
        "prevention_action": item.prevention_action,
        "status": item.status,
        "owner": getattr(item, "owner", "") or "",
        "due_date": getattr(item, "due_date", "") or "",
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }
