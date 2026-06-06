from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ActivityLog, Decision, InboxItem, RiskEvent, WorkItem


def log_activity(db: Session, action: str, message: str, project_id: int | None = None) -> ActivityLog:
    log = ActivityLog(project_id=project_id, action=action, message=message)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def today_focus(db: Session, project_id: int) -> dict:
    inbox = list(db.scalars(select(InboxItem).where(InboxItem.project_id == project_id, InboxItem.status == "Open")).all())
    risks = list(db.scalars(select(RiskEvent).where(RiskEvent.project_id == project_id, RiskEvent.blocking.is_(True))).all())
    bugs = list(db.scalars(select(WorkItem).where(WorkItem.project_id == project_id, WorkItem.kind == "bug", WorkItem.status != "Closed")).all())
    return {"project_id": project_id, "open_inbox": inbox[:5], "blocking_risks": risks[:5], "open_bugs": bugs[:5], "next_actions": _next_actions(inbox, risks, bugs)}


def count_inbox_open(db: Session, project_id: int) -> int:
    stmt = select(func.count()).select_from(InboxItem).where(InboxItem.project_id == project_id, InboxItem.status == "Open")
    return int(db.scalar(stmt) or 0)


def count_decisions(db: Session, project_id: int) -> int:
    stmt = select(func.count()).select_from(Decision).where(Decision.project_id == project_id)
    return int(db.scalar(stmt) or 0)


def _next_actions(inbox, risks, bugs) -> list[str]:
    actions = []
    if inbox:
        actions.append("Triage open inbox items.")
    if risks:
        actions.append("Resolve blocking risks before release.")
    if bugs:
        actions.append("Fix or close open bugs.")
    return actions or ["No urgent blockers. Prepare evidence report."]
