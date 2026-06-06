from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Requirement, RiskEvent, WorkItem
from app.rules import readiness_score
from app.services import run_risk_scan


def release_risk_dashboard(db: Session, project_id: int) -> dict:
    risks = run_risk_scan(db, project_id)
    requirements = db.scalars(select(Requirement).where(Requirement.project_id == project_id)).all()
    grouped = []
    for req in requirements:
        if req.status == "Archived":
            continue
        req_risks = [risk for risk in risks if risk.requirement_id == req.id]
        grouped.append(_requirement_dashboard_row(req, req_risks))
    grouped.sort(key=lambda row: (_severity_rank(row["highest_severity"]), row["blocking_risks"], row["risk_count"]), reverse=True)
    blocking = sum(row["blocking_risks"] for row in grouped)
    return {
        "project_id": project_id,
        "total_requirements": len(grouped),
        "total_risks": sum(row["risk_count"] for row in grouped),
        "blocking_risks": blocking,
        "release_status": "Blocked" if blocking else "Watch" if any(row["risk_count"] for row in grouped) else "Safe",
        "requirements": grouped,
        "top_actions": _top_actions(grouped),
    }


def requirement_risk_drilldown(db: Session, requirement: Requirement) -> dict:
    if requirement.status == "Archived":
        return _archived_drilldown(requirement)
    all_risks = run_risk_scan(db, requirement.project_id)
    req_risks = [risk for risk in all_risks if risk.requirement_id == requirement.id]
    items = list(db.scalars(select(WorkItem).where(WorkItem.requirement_id == requirement.id)).all())
    return {
        "requirement_id": requirement.id,
        "requirement_key": requirement.key,
        "requirement_title": requirement.title,
        "priority": requirement.priority,
        "status": requirement.status,
        "score": readiness_score([_risk_dict(risk) for risk in req_risks]),
        "risk_count": len(req_risks),
        "blocking_risks": sum(1 for risk in req_risks if risk.blocking),
        "highest_severity": _highest_severity(req_risks),
        "risks": [_risk_dict(risk) for risk in req_risks],
        "linked_work_items": [_work_item_dict(item) for item in items],
        "missing_placeholders": _missing_placeholders(req_risks),
        "next_actions": _fix_hints(req_risks) or ["No missing task/test placeholder is needed right now."],
    }


def _requirement_dashboard_row(req: Requirement, req_risks: list[RiskEvent]) -> dict:
    return {
        "requirement_id": req.id,
        "requirement_key": req.key,
        "requirement_title": req.title,
        "priority": req.priority,
        "status": req.status,
        "score": readiness_score([_risk_dict(risk) for risk in req_risks]),
        "risk_count": len(req_risks),
        "blocking_risks": sum(1 for risk in req_risks if risk.blocking),
        "highest_severity": _highest_severity(req_risks),
        "fix_hints": _fix_hints(req_risks),
        "risks": [_risk_dict(risk) for risk in req_risks],
    }


def _archived_drilldown(requirement: Requirement) -> dict:
    return {
        "requirement_id": requirement.id,
        "requirement_key": requirement.key,
        "requirement_title": requirement.title,
        "status": requirement.status,
        "score": 100,
        "risks": [],
        "linked_work_items": [],
        "missing_placeholders": [],
        "next_actions": ["Requirement is archived, so release-risk scan ignores it."],
    }


def _risk_dict(risk: RiskEvent) -> dict:
    return {"rule_id": risk.rule_id, "title": risk.title, "message": risk.message, "severity": risk.severity, "blocking": risk.blocking}


def _highest_severity(risks: list[RiskEvent]) -> str:
    return max((risk.severity for risk in risks), key=_severity_rank, default="Low")


def _severity_rank(severity: str) -> int:
    return {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}.get(severity, 0)


def _fix_hints(risks: list[RiskEvent]) -> list[str]:
    hints = {
        "critical_requirement_without_test": "Add or finish one linked test WorkItem before release.",
        "requirement_without_task": "Create or link one implementation task for this requirement.",
        "open_blocking_bug": "Fix, close, or downgrade linked high/critical bugs.",
    }
    return sorted({hints.get(risk.rule_id, "Review and resolve this requirement risk.") for risk in risks})


def _missing_placeholders(risks: list[RiskEvent]) -> list[dict]:
    rule_ids = {risk.rule_id for risk in risks}
    placeholders = []
    if "requirement_without_task" in rule_ids:
        placeholders.append({"kind": "task", "title": "Create implementation task placeholder", "reason": "This requirement has no linked implementation task yet."})
    if "critical_requirement_without_test" in rule_ids:
        placeholders.append({"kind": "test", "title": "Create test coverage placeholder", "reason": "This high/critical requirement has no linked test yet."})
    return placeholders


def _top_actions(rows: list[dict]) -> list[str]:
    actions = []
    for row in rows:
        for hint in row["fix_hints"]:
            actions.append(f"{row['requirement_key']}: {hint}")
    return actions[:5] or ["No blocking release-risk action needed right now."]


def _work_item_dict(item: WorkItem) -> dict:
    return {"id": item.id, "kind": item.kind, "title": item.title, "status": item.status, "severity": item.severity, "requirement_id": item.requirement_id}
