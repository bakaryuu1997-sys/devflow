from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import GitItem, TraceLink, WorkItem


def workload_dashboard(db: Session, project_id: int) -> list[dict]:
    owners = defaultdict(lambda: {"open_items": 0, "high_or_critical": 0, "risky_git_items": 0})

    work_items = db.scalars(select(WorkItem).where(WorkItem.project_id == project_id)).all()
    for item in work_items:
        owner = "unassigned"
        if item.status != "Closed":
            owners[owner]["open_items"] += 1
        if item.severity in {"High", "Critical", "Blocker"}:
            owners[owner]["high_or_critical"] += 1

    git_items = db.scalars(select(GitItem).where(GitItem.project_id == project_id)).all()
    for item in git_items:
        owner = item.author or "unknown"
        if item.risk in {"High", "Critical"}:
            owners[owner]["risky_git_items"] += 1

    return [
        {
            "owner": owner,
            "open_items": data["open_items"],
            "high_or_critical": data["high_or_critical"],
            "risky_git_items": data["risky_git_items"],
            "risk": _risk(data),
        }
        for owner, data in sorted(owners.items())
    ]


def _risk(data: dict) -> str:
    if data["high_or_critical"] >= 3 or data["risky_git_items"] >= 3:
        return "Critical"
    if data["high_or_critical"] > 0 or data["risky_git_items"] > 0 or data["open_items"] >= 5:
        return "High"
    if data["open_items"] > 0:
        return "Medium"
    return "Low"
