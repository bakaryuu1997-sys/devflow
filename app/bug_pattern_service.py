from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TraceLink, WorkItem


def bug_pattern_dashboard(db: Session, project_id: int) -> list[dict]:
    modules = defaultdict(lambda: {"open_bugs": 0, "critical_or_high": 0, "reopened": 0})
    work_bugs = db.scalars(select(WorkItem).where(WorkItem.project_id == project_id, WorkItem.kind == "bug")).all()
    linked_bugs = db.scalars(
        select(TraceLink).where(TraceLink.project_id == project_id, TraceLink.link_type == "bug")
    ).all()

    for bug in work_bugs:
        module = "general"
        if bug.status != "Closed":
            modules[module]["open_bugs"] += 1
        if bug.severity in {"Critical", "High", "Blocker"}:
            modules[module]["critical_or_high"] += 1

    for bug in linked_bugs:
        module = bug.module or "general"
        if bug.status != "Closed":
            modules[module]["open_bugs"] += 1
        if "critical" in bug.title.lower() or "high" in bug.title.lower():
            modules[module]["critical_or_high"] += 1
        if "reopen" in bug.status.lower() or "reopen" in bug.title.lower():
            modules[module]["reopened"] += 1

    return [
        {
            "module": module,
            "open_bugs": data["open_bugs"],
            "critical_or_high": data["critical_or_high"],
            "reopened": data["reopened"],
            "risk": _risk(data),
        }
        for module, data in sorted(modules.items())
    ]


def _risk(data: dict) -> str:
    if data["critical_or_high"] >= 3 or data["reopened"] >= 2:
        return "Critical"
    if data["critical_or_high"] > 0 or data["open_bugs"] >= 3:
        return "High"
    if data["open_bugs"] > 0:
        return "Medium"
    return "Low"
