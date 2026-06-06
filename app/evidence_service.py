from sqlalchemy import select
from sqlalchemy.orm import Session

from app.guard_service import list_findings
from app.models import ActivityLog, GitItem, Release, Requirement, RequirementDiff, RiskEvent, TraceLink, WorkItem


def build_evidence_markdown(db: Session, project_id: int, release_id: int | None = None) -> str:
    release = db.get(Release, release_id) if release_id else None
    requirements = db.scalars(select(Requirement).where(Requirement.project_id == project_id)).all()
    work_items = db.scalars(select(WorkItem).where(WorkItem.project_id == project_id)).all()
    risks = db.scalars(select(RiskEvent).where(RiskEvent.project_id == project_id)).all()
    guards = list_findings(db, project_id)
    activity = db.scalars(select(ActivityLog).where(ActivityLog.project_id == project_id).order_by(ActivityLog.id.desc())).all()
    trace_links = db.scalars(select(TraceLink).where(TraceLink.project_id == project_id)).all()
    git_items = db.scalars(select(GitItem).where(GitItem.project_id == project_id)).all()
    diffs = db.scalars(select(RequirementDiff).where(RequirementDiff.project_id == project_id)).all()

    return "\n".join([
        "# Release Evidence Report",
        "",
        f"Project ID: {project_id}",
        f"Release: {release.version if release else 'N/A'}",
        f"Readiness score: {release.readiness_score if release else 'N/A'}",
        f"Gate passed: {release.gate_passed if release else 'N/A'}",
        "",
        "## Requirements",
        *_lines(requirements, lambda x: f"- {x.key}: {x.title} ({x.priority}/{x.status})"),
        "",
        "## Traceability Links",
        *_lines(trace_links, lambda x: f"- {x.requirement_key} → {x.link_type}:{x.target_key} ({x.status})"),
        "",
        "## Requirement Diffs",
        *_lines(diffs, lambda x: f"- {x.requirement_key} {x.change_type}: {x.risk} — {x.message}"),
        "",
        "## Git Evidence",
        *_lines(git_items, lambda x: f"- {x.item_type} {x.ref}: {x.title} by {x.author} risk={x.risk}"),
        "",
        "## Work Items",
        *_lines(work_items, lambda x: f"- {x.kind}: {x.title} ({x.status}/{x.severity})"),
        "",
        "## Risks",
        *_lines(risks, lambda x: f"- {x.severity}: {x.title} blocking={x.blocking}"),
        "",
        "## Guard Findings",
        *_lines(guards, lambda x: f"- {x.guard_type} {x.severity}: {x.title} blocking={x.blocking} — {x.message}"),
        "",
        "## Recent Activity",
        *_lines(activity[:10], lambda x: f"- {x.action}: {x.message}"),
    ])


def _lines(items, formatter):
    return [formatter(item) for item in items] or ["- None"]
