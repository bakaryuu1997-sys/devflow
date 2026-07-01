from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.guard_service import blocking_guard_count
from app.models import Project, Release, Requirement, RiskEvent, WorkItem
from app.os_service import count_decisions, count_inbox_open, log_activity
from app.rules import quality_gate, readiness_score, recommendations, risk_rules


def get_project_or_none(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def create_project(db: Session, name: str, description: str = "") -> Project:
    project = Project(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    log_activity(db, "project.created", f"Created project {project.name}", project.id)
    return project


def run_risk_scan(db: Session, project_id: int) -> list[RiskEvent]:
    db.execute(delete(RiskEvent).where(RiskEvent.project_id == project_id))
    requirements = db.scalars(
        select(Requirement).where(Requirement.project_id == project_id, Requirement.status != "Archived")
    ).all()
    created = []
    for req in requirements:
        items = db.scalars(select(WorkItem).where(WorkItem.requirement_id == req.id)).all()
        item_dicts = [{"kind": item.kind, "status": item.status, "severity": item.severity} for item in items]
        for risk in risk_rules({"priority": req.priority}, item_dicts):
            event = RiskEvent(project_id=project_id, requirement_id=req.id, **risk)
            db.add(event)
            created.append(event)
    db.commit()
    for event in created:
        db.refresh(event)
    log_activity(db, "risk.scan", f"Risk scan created {len(created)} event(s)", project_id)
    return created


def dashboard(db: Session, project_id: int) -> dict:
    return {
        "project_id": project_id,
        "requirements": _count_active_requirements(db, project_id),
        "tasks": _count_work(db, project_id, "task"),
        "tests": _count_work(db, project_id, "test"),
        "bugs": _count_work(db, project_id, "bug"),
        "inbox_open": count_inbox_open(db, project_id),
        "decisions": count_decisions(db, project_id),
        "open_risks": _count(db, RiskEvent, project_id),
        "blocking_risks": _count_blocking_risks(db, project_id),
    }


def calculate_readiness(db: Session, release: Release) -> dict:
    risks = run_risk_scan(db, release.project_id)
    risk_dicts = [{"rule_id": r.rule_id, "severity": r.severity, "blocking": r.blocking} for r in risks]
    score = readiness_score(risk_dicts)
    blockers = sum(1 for risk in risks if risk.blocking) + blocking_guard_count(db, release.project_id)
    passed = quality_gate(score, blockers)
    release.readiness_score = score
    release.gate_passed = passed
    release.status = "Ready" if passed else "Blocked"
    db.commit()
    db.refresh(release)
    log_activity(
        db, "release.readiness", f"Release {release.version} score={score} passed={passed}", release.project_id
    )
    return {
        "release_id": release.id,
        "score": score,
        "blocking_risks": blockers,
        "passed": passed,
        "recommendations": recommendations(risk_dicts),
    }


def _count_active_requirements(db: Session, project_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Requirement)
        .where(Requirement.project_id == project_id, Requirement.status != "Archived")
    )
    return int(db.scalar(stmt) or 0)


def _count(db: Session, model, project_id: int) -> int:
    stmt = select(func.count()).select_from(model).where(model.project_id == project_id)
    return int(db.scalar(stmt) or 0)


def _count_work(db: Session, project_id: int, kind: str) -> int:
    stmt = select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id, WorkItem.kind == kind)
    return int(db.scalar(stmt) or 0)


def _count_blocking_risks(db: Session, project_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(RiskEvent)
        .where(RiskEvent.project_id == project_id, RiskEvent.blocking.is_(True))
    )
    return int(db.scalar(stmt) or 0)
