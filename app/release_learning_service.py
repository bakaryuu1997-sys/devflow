from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem, ReleaseRetrospective
from app.release_learning_helpers import (
    DONE_STATUSES,
    generated_prevention_items,
    merge_checklist,
    recurring_risk_signals,
    signal_lines,
)
from app.release_risk_dashboard_service import release_risk_dashboard


def release_learning_loop(db: Session, project_id: int) -> dict:
    project = db.get(Project, project_id)
    retrospectives = _retrospectives(db, project_id)
    saved_items = _saved_items(db, project_id)
    risk_dashboard = release_risk_dashboard(db, project_id)
    generated = generated_prevention_items(retrospectives, risk_dashboard)
    open_saved = [item for item in saved_items if item["status"] not in DONE_STATUSES]
    checklist = merge_checklist(generated, open_saved)
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "retrospective_count": len(retrospectives),
        "saved_item_count": len(saved_items),
        "open_saved_item_count": len(open_saved),
        "recurring_risk_signals": recurring_risk_signals(risk_dashboard),
        "generated_prevention_items": generated,
        "saved_prevention_items": saved_items,
        "prevention_checklist": checklist,
    }
    data["content"] = learning_loop_markdown(data)
    return data


def create_learning_item(
    db: Session,
    project_id: int,
    title: str,
    prevention_action: str,
    source: str = "manual",
    status: str = "Open",
    owner: str = "",
    due_date: str = "",
) -> dict:
    item = ReleaseLearningItem(
        project_id=project_id,
        source=source.strip() or "manual",
        title=title.strip() or "Untitled prevention item",
        prevention_action=prevention_action.strip() or "Define a concrete prevention action before the next release.",
        status=status.strip() or "Open",
        owner=owner.strip(),
        due_date=due_date.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"created": True, "message": "Release learning item saved.", "item": _learning_item_dict(item)}


def update_learning_item_status(db: Session, item_id: int, status: str) -> dict | None:
    item = db.get(ReleaseLearningItem, item_id)
    if not item:
        return None
    item.status = status.strip() or item.status
    db.commit()
    db.refresh(item)
    return {"updated": True, "message": "Release learning item status updated.", "item": _learning_item_dict(item)}


def update_learning_item_planning(
    db: Session,
    item_id: int,
    owner: str | None = None,
    due_date: str | None = None,
    status: str | None = None,
) -> dict | None:
    item = db.get(ReleaseLearningItem, item_id)
    if not item:
        return None
    if owner is not None:
        item.owner = owner.strip()
    if due_date is not None:
        item.due_date = due_date.strip()
    if status is not None:
        item.status = status.strip() or item.status
    db.commit()
    db.refresh(item)
    return {"updated": True, "message": "Release learning item planning updated.", "item": _learning_item_dict(item)}


def learning_loop_markdown(data: dict) -> str:
    lines = [
        "# Release Learning Loop & Risk Prevention Checklist",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Retrospectives reviewed: {data['retrospective_count']}",
        f"Saved prevention items: {data['saved_item_count']}",
        "",
        "## Recurring risk signals",
    ]
    lines.extend(signal_lines(data["recurring_risk_signals"]))
    lines.extend(["", "## Prevention checklist"])
    lines.extend(_checklist_lines(data["prevention_checklist"]))
    lines.extend(["", "## Saved learning items"])
    lines.extend(_saved_lines(data["saved_prevention_items"]))
    return "\n".join(lines).strip() + "\n"


def _retrospectives(db: Session, project_id: int) -> list[ReleaseRetrospective]:
    return list(
        db.scalars(
            select(ReleaseRetrospective)
            .where(ReleaseRetrospective.project_id == project_id)
            .order_by(ReleaseRetrospective.created_at.desc())
        ).all()
    )


def _saved_items(db: Session, project_id: int) -> list[dict]:
    items = db.scalars(
        select(ReleaseLearningItem)
        .where(ReleaseLearningItem.project_id == project_id)
        .order_by(ReleaseLearningItem.created_at.desc())
    ).all()
    return [_learning_item_dict(item) for item in items]


def _checklist_lines(items: list[dict]) -> list[str]:
    if not items:
        return ["- [ ] No recurring risk prevention item is needed right now."]
    return [
        f"- [ ] {item['title']} — {item['prevention_action']} ({item['source']}; owner={item.get('owner') or 'Unassigned'}; due={item.get('due_date') or 'No due date'})"
        for item in items
    ]


def _saved_lines(items: list[dict]) -> list[str]:
    if not items:
        return ["- No saved learning items yet."]
    rows = []
    for item in items:
        checked = "x" if item["status"] in DONE_STATUSES else " "
        rows.append(
            f"- [{checked}] #{item['id']} {item['title']} — {item['prevention_action']} | "
            f"status={item['status']} | owner={item.get('owner') or 'Unassigned'} | due={item.get('due_date') or 'No due date'}"
        )
    return rows


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
