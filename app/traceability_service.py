from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Requirement, TraceLink, WorkItem


def create_trace_link(db: Session, project_id: int, data) -> TraceLink:
    link = TraceLink(project_id=project_id, **data.model_dump())
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def list_trace_links(db: Session, project_id: int) -> list[TraceLink]:
    stmt = select(TraceLink).where(TraceLink.project_id == project_id).order_by(TraceLink.id.desc())
    return list(db.scalars(stmt).all())


def traceability_matrix(db: Session, project_id: int) -> list[dict]:
    requirements = db.scalars(select(Requirement).where(Requirement.project_id == project_id)).all()
    work_items = db.scalars(select(WorkItem).where(WorkItem.project_id == project_id)).all()
    links = db.scalars(select(TraceLink).where(TraceLink.project_id == project_id)).all()
    rows = []

    for req in requirements:
        req_work = [item for item in work_items if item.requirement_id == req.id]
        req_links = [link for link in links if link.requirement_key == req.key]
        task_count = _unique_count(req_work, req_links, "task")
        test_count = _unique_count(req_work, req_links, "test")
        bug_count = _unique_count(req_work, req_links, "bug")
        api_count = _count_links(req_links, "api")
        commit_count = _count_links(req_links, "commit")
        warnings = _warnings(req.priority, task_count, test_count, bug_count)
        rows.append({
            "requirement_key": req.key,
            "requirement_title": req.title,
            "task_count": task_count,
            "api_count": api_count,
            "test_count": test_count,
            "bug_count": bug_count,
            "commit_count": commit_count,
            "risk": _risk(req.priority, test_count, bug_count, warnings),
            "warnings": warnings,
        })
    return rows


def _unique_count(work_items, links, kind: str) -> int:
    keys = set()
    for item in work_items:
        if item.kind == kind:
            keys.add(_normalize(item.title))
    for link in links:
        if link.link_type == kind:
            keys.add(_normalize(link.target_key or link.title))
    return len(keys)


def _count_links(links, link_type: str) -> int:
    return len({_normalize(link.target_key or link.title) for link in links if link.link_type == link_type})


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _warnings(priority: str, task_count: int, test_count: int, bug_count: int) -> list[str]:
    warnings = []
    if task_count == 0:
        warnings.append("No implementation task linked.")
    if priority in {"Critical", "High"} and test_count == 0:
        warnings.append("High/Critical requirement has no test case.")
    if bug_count > 0:
        warnings.append("Requirement has linked bug(s).")
    return warnings


def _risk(priority: str, test_count: int, bug_count: int, warnings: list[str]) -> str:
    if bug_count >= 3:
        return "Critical"
    if priority in {"Critical", "High"} and test_count == 0:
        return "High"
    if warnings:
        return "Medium"
    return "Low"
