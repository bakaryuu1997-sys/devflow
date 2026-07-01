from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseLearningItem
from app.release_recurring_risk_service import recurring_risk_trends

SEVERITY_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
DONE_STATUSES = {"Done", "Prevented", "Closed"}


def risk_prevention_backlog(db: Session, project_id: int, limit: int = 5) -> dict:
    project = db.get(Project, project_id)
    trends = recurring_risk_trends(db, project_id, limit)
    saved = _saved_learning_items(db, project_id)
    rows = [_backlog_row(risk, saved) for risk in trends.get("recurring_risks", [])]
    rows.sort(
        key=lambda row: (
            row["already_saved"],
            -_priority_rank(row["priority"]),
            -row["snapshot_occurrences"],
            row["rule_id"],
        )
    )
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "snapshot_count": trends.get("snapshot_count", 0),
        "can_analyze": trends.get("can_analyze", False),
        "recurring_risk_count": len(trends.get("recurring_risks", [])),
        "open_backlog_count": sum(1 for row in rows if not row["already_saved"]),
        "saved_backlog_count": sum(1 for row in rows if row["already_saved"]),
        "backlog_items": rows,
        "action_hints": _action_hints(rows),
    }
    data["content"] = prevention_backlog_markdown(data)
    return data


def auto_create_learning_items_from_backlog(db: Session, project_id: int, limit: int = 5) -> dict:
    data = risk_prevention_backlog(db, project_id, limit)
    created = []
    skipped = []
    for row in data.get("backlog_items", []):
        if row.get("already_saved"):
            skipped.append(
                {"rule_id": row["rule_id"], "reason": "already_saved", "learning_item_id": row.get("learning_item_id")}
            )
            continue
        item = ReleaseLearningItem(
            project_id=project_id,
            source=row["source"],
            title=row["title"],
            prevention_action=row["prevention_action"],
            status="Open",
            owner="",
            due_date="",
        )
        db.add(item)
        db.flush()
        created.append(_learning_item_dict(item))
    db.commit()
    for item in created:
        db.refresh(db.get(ReleaseLearningItem, item["id"]))
    refreshed = risk_prevention_backlog(db, project_id, limit)
    return {
        "created": len(created),
        "skipped": len(skipped),
        "created_items": created,
        "skipped_items": skipped,
        "backlog": refreshed,
        "message": f"Created {len(created)} prevention learning item(s); skipped {len(skipped)} existing item(s).",
    }


def prevention_backlog_markdown(data: dict) -> str:
    if not data.get("can_analyze"):
        return "# Risk Prevention Backlog\n\nCreate at least two release sign-off snapshots before generating a prevention backlog.\n"
    lines = [
        "# Risk Prevention Backlog",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Snapshots analyzed: {data['snapshot_count']}",
        f"Recurring risks: {data['recurring_risk_count']}",
        f"Open backlog items: {data['open_backlog_count']}",
        "",
        "## Action hints",
    ]
    lines.extend(
        [f"- {hint}" for hint in data.get("action_hints", [])]
        or ["- No recurring risk backlog item is needed right now."]
    )
    lines.extend(["", "## Backlog"])
    if not data.get("backlog_items"):
        lines.append("- No recurring risk prevention backlog item yet.")
    for item in data.get("backlog_items", []):
        checked = "x" if item.get("already_saved") else " "
        lines.append(
            f"- [{checked}] {item['rule_id']} · {item['title']} | priority={item['priority']} | "
            f"snapshots={item['snapshot_occurrences']} | action={item['prevention_action']}"
        )
    return "\n".join(lines).strip() + "\n"


def _saved_learning_items(db: Session, project_id: int) -> dict[str, ReleaseLearningItem]:
    rows = db.scalars(
        select(ReleaseLearningItem)
        .where(ReleaseLearningItem.project_id == project_id)
        .order_by(ReleaseLearningItem.created_at.desc())
    ).all()
    result = {}
    for item in rows:
        if item.source.startswith("recurring-risk:") and item.status not in DONE_STATUSES:
            result.setdefault(item.source, item)
    return result


def _backlog_row(risk: dict, saved: dict[str, ReleaseLearningItem]) -> dict:
    source = f"recurring-risk:{risk.get('rule_id', 'unknown')}"
    saved_item = saved.get(source)
    priority = _priority(risk)
    title = f"Prevent recurring risk: {risk.get('latest_title') or risk.get('title') or risk.get('rule_id')}"
    action = _prevention_action(risk, priority)
    return {
        "rule_id": risk.get("rule_id", "unknown"),
        "source": source,
        "title": title,
        "prevention_action": action,
        "priority": priority,
        "latest_severity": risk.get("latest_severity", "Low"),
        "snapshot_occurrences": risk.get("snapshot_occurrences", 0),
        "blocking_occurrences": risk.get("blocking_occurrences", 0),
        "total_events": risk.get("total_events", 0),
        "affected_requirements": risk.get("affected_requirements", []),
        "seen_in_snapshots": risk.get("seen_in_snapshots", []),
        "already_saved": saved_item is not None,
        "learning_item_id": saved_item.id if saved_item else None,
        "learning_item_status": saved_item.status if saved_item else None,
    }


def _priority(risk: dict) -> str:
    if risk.get("blocking_occurrences", 0) > 0 or _severity_rank(risk.get("latest_severity")) >= 4:
        return "Critical"
    if risk.get("snapshot_occurrences", 0) >= 3 or _severity_rank(risk.get("latest_severity")) >= 3:
        return "High"
    if risk.get("snapshot_occurrences", 0) >= 2:
        return "Medium"
    return "Low"


def _prevention_action(risk: dict, priority: str) -> str:
    affected = ", ".join(risk.get("affected_requirements", [])[:5]) or "affected requirements"
    if risk.get("blocking_occurrences", 0) > 0:
        return (
            f"Add a mandatory pre-signoff gate for {affected}; this recurring risk has blocked at least one snapshot."
        )
    if priority in {"Critical", "High"}:
        return f"Create owner/checklist coverage for {affected} before the next release review starts."
    return f"Track {affected} in the next release review and close the prevention item once the risk stops recurring."


def _action_hints(rows: list[dict]) -> list[str]:
    if not rows:
        return ["No recurring risk backlog item is needed right now."]
    open_rows = [row for row in rows if not row["already_saved"]]
    if not open_rows:
        return ["All current recurring risks already have open prevention learning items."]
    return [
        f"Create prevention item for {row['rule_id']} ({row['priority']}) before the next release planning session."
        for row in open_rows[:5]
    ]


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


def _priority_rank(priority: str) -> int:
    return {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}.get(priority, 0)


def _severity_rank(severity: str | None) -> int:
    return SEVERITY_RANK.get(severity or "Low", 0)
