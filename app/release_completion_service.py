from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Requirement, RequirementReview, RiskEvent, WorkItem
from app.services import run_risk_scan
from app.time_utils import utc_now

DONE_STATUSES = {"Done", "Closed"}
HIGH_PRIORITIES = {"High", "Critical"}
OPEN_STATUSES = {"Open", "In Progress"}
HIGH_SEVERITIES = {"High", "Critical"}


def project_release_review_completion(db: Session, project_id: int) -> dict:
    risks = run_risk_scan(db, project_id)
    requirements = list(db.scalars(select(Requirement).where(Requirement.project_id == project_id)).all())
    rows = []
    for requirement in requirements:
        if requirement.status == "Archived":
            continue
        rows.append(requirement_done_gates(db, requirement, risks))
    total = len(rows)
    done = sum(1 for row in rows if row["is_done"])
    reviewed = sum(1 for row in rows if row["review_complete"])
    blocked = sum(1 for row in rows if row["blocking_risks"])
    return {
        "project_id": project_id,
        "total_requirements": total,
        "done_requirements": done,
        "reviewed_requirements": reviewed,
        "blocking_requirements": blocked,
        "completion_percent": _percent(done, total),
        "review_percent": _percent(reviewed, total),
        "release_review_complete": bool(total and reviewed == total and done == total and blocked == 0),
        "requirements": rows,
        "next_actions": _next_actions(rows),
    }


def requirement_done_gates(db: Session, requirement: Requirement, project_risks: list[RiskEvent] | None = None) -> dict:
    risks = project_risks if project_risks is not None else run_risk_scan(db, requirement.project_id)
    req_risks = [risk for risk in risks if risk.requirement_id == requirement.id]
    items = list(db.scalars(select(WorkItem).where(WorkItem.requirement_id == requirement.id)).all())
    review = _review_for(db, requirement.id)
    gates = _gates(requirement, items, req_risks)
    is_done = all(gate["passed"] for gate in gates)
    return {
        "requirement_id": requirement.id,
        "requirement_key": requirement.key,
        "requirement_title": requirement.title,
        "priority": requirement.priority,
        "status": requirement.status,
        "is_done": is_done,
        "review_complete": bool(review and review.is_complete),
        "review_completed_at": review.completed_at.isoformat() if review and review.completed_at else None,
        "blocking_risks": sum(1 for risk in req_risks if risk.blocking),
        "open_high_bugs": sum(1 for item in items if _is_open_high_bug(item)),
        "linked_items": len(items),
        "done_items": sum(1 for item in items if item.status in DONE_STATUSES),
        "gates": gates,
    }


def mark_requirement_review_complete(db: Session, requirement: Requirement) -> dict:
    data = requirement_done_gates(db, requirement)
    if not data["is_done"]:
        return {**data, "marked": False, "message": "Requirement gates must pass before review can be completed."}
    review = _review_for(db, requirement.id)
    if not review:
        review = RequirementReview(project_id=requirement.project_id, requirement_id=requirement.id)
        db.add(review)
    review.is_complete = True
    review.completed_at = utc_now()
    db.commit()
    return {**requirement_done_gates(db, requirement), "marked": True, "message": "Requirement review completed."}


def reopen_requirement_review(db: Session, requirement: Requirement) -> dict:
    review = _review_for(db, requirement.id)
    if not review:
        review = RequirementReview(project_id=requirement.project_id, requirement_id=requirement.id)
        db.add(review)
    review.is_complete = False
    review.completed_at = None
    db.commit()
    return {**requirement_done_gates(db, requirement), "marked": False, "message": "Requirement review reopened."}


def _gates(requirement: Requirement, items: list[WorkItem], risks: list[RiskEvent]) -> list[dict]:
    has_done_task = any(item.kind == "task" and item.status in DONE_STATUSES for item in items)
    has_done_test = any(item.kind == "test" and item.status in DONE_STATUSES for item in items)
    high_priority = requirement.priority in HIGH_PRIORITIES
    no_open_high_bugs = not any(_is_open_high_bug(item) for item in items)
    no_blocking_risks = not any(risk.blocking for risk in risks)
    gates = [
        _gate("done_task", has_done_task, "At least one linked task is Done or Closed."),
        _gate("no_open_high_bug", no_open_high_bugs, "No linked open High/Critical bug remains."),
        _gate("no_blocking_risk", no_blocking_risks, "No active blocking release-risk remains."),
    ]
    if high_priority:
        gates.insert(1, _gate("done_test", has_done_test, "High/Critical requirement has at least one Done or Closed test."))
    else:
        gates.insert(1, _gate("done_test_optional", True, "Test gate is optional for Low/Medium requirements."))
    return gates


def _gate(key: str, passed: bool, label: str) -> dict:
    return {"key": key, "passed": passed, "label": label}


def _is_open_high_bug(item: WorkItem) -> bool:
    return item.kind == "bug" and item.status in OPEN_STATUSES and item.severity in HIGH_SEVERITIES


def _review_for(db: Session, requirement_id: int) -> RequirementReview | None:
    return db.scalars(select(RequirementReview).where(RequirementReview.requirement_id == requirement_id)).first()


def _percent(value: int, total: int) -> int:
    if not total:
        return 100
    return round((value / total) * 100)


def _next_actions(rows: list[dict]) -> list[str]:
    actions = []
    for row in rows:
        if row["review_complete"]:
            continue
        failed = [gate["label"] for gate in row["gates"] if not gate["passed"]]
        if failed:
            actions.append(f"{row['requirement_key']}: {failed[0]}")
        elif row["is_done"]:
            actions.append(f"{row['requirement_key']}: Mark requirement review complete.")
    return actions[:5] or ["All active requirements are reviewed and release gates are complete."]
