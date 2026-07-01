from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RequirementChange, TraceLink


def record_requirement_change(db: Session, project_id: int, payload) -> RequirementChange:
    changed_fields = detect_changed_fields(payload.old_text, payload.new_text)
    row = RequirementChange(
        project_id=project_id,
        requirement_key=payload.requirement_key,
        old_text=payload.old_text,
        new_text=payload.new_text,
        changed_fields=", ".join(changed_fields),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_requirement_changes(db: Session, project_id: int) -> list[RequirementChange]:
    stmt = (
        select(RequirementChange)
        .where(RequirementChange.project_id == project_id)
        .order_by(RequirementChange.id.desc())
    )
    return list(db.scalars(stmt).all())


def detect_changed_fields(old: str, new: str) -> list[str]:
    fields = []
    old_l = old.lower()
    new_l = new.lower()
    keywords = {
        "auth": ["login", "password", "email", "phone", "token"],
        "payment": ["payment", "invoice", "card", "callback"],
        "database": ["store", "save", "delete", "phone", "address"],
        "api": ["api", "endpoint", "request", "response"],
        "ui": ["screen", "form", "button", "page"],
    }
    for field, words in keywords.items():
        if any(word in new_l for word in words) and old_l != new_l:
            fields.append(field)
    return fields or ["general"]


def analyze_impact(db: Session, project_id: int, requirement_key: str) -> dict:
    links = list(
        db.scalars(
            select(TraceLink).where(
                TraceLink.project_id == project_id,
                TraceLink.requirement_key == requirement_key,
            )
        ).all()
    )
    return {
        "requirement_key": requirement_key,
        "impacted_tasks": _targets(links, "task"),
        "impacted_apis": _targets(links, "api"),
        "impacted_tests": _targets(links, "test"),
        "impacted_bugs": _targets(links, "bug"),
        "suggested_actions": _suggestions(links),
    }


def _targets(links, link_type: str) -> list[str]:
    return [f"{link.target_key}: {link.title or link.status}" for link in links if link.link_type == link_type]


def _suggestions(links) -> list[str]:
    suggestions = ["Review changed requirement with owner."]
    if any(link.link_type == "api" for link in links):
        suggestions.append("Retest related API endpoints and update API docs.")
    if any(link.link_type == "test" for link in links):
        suggestions.append("Update and rerun linked test cases.")
    if any(link.link_type == "task" for link in links):
        suggestions.append("Reopen or verify linked tasks.")
    if any(link.link_type == "bug" for link in links):
        suggestions.append("Check whether linked bugs are still valid.")
    return suggestions
