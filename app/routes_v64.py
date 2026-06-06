from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.models import Requirement, WorkItem
from app.release_risk_dashboard_service import requirement_risk_drilldown
from app.schemas import WorkItemPlaceholderCreate, WorkItemRead

router = APIRouter(prefix="/api", tags=["v6-4-risk-drilldown"])


@router.get("/requirements/{requirement_id}/risk-drilldown")
def api_requirement_risk_drilldown(requirement_id: int, db: Session = Depends(get_db)):
    requirement = db.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")
    return requirement_risk_drilldown(db, requirement)


@router.post("/requirements/{requirement_id}/work-item-placeholders", response_model=WorkItemRead)
def api_create_requirement_work_item_placeholder(
    requirement_id: int,
    payload: WorkItemPlaceholderCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_write),
):
    requirement = db.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")
    _validate_placeholder(requirement, payload.kind)
    existing = _existing_placeholder(db, requirement, payload.kind)
    if existing:
        return existing
    item = _new_placeholder(requirement, payload.kind)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _validate_placeholder(requirement: Requirement, kind: str) -> None:
    if requirement.status == "Archived":
        raise HTTPException(400, "Cannot create placeholders for archived requirements")
    if kind not in {"task", "test"}:
        raise HTTPException(400, "Placeholder kind must be task or test")


def _existing_placeholder(db: Session, requirement: Requirement, kind: str) -> WorkItem | None:
    return db.scalars(
        select(WorkItem).where(
            WorkItem.project_id == requirement.project_id,
            WorkItem.requirement_id == requirement.id,
            WorkItem.kind == kind,
        )
    ).first()


def _new_placeholder(requirement: Requirement, kind: str) -> WorkItem:
    title_prefix = "Implementation task" if kind == "task" else "Test coverage"
    return WorkItem(
        project_id=requirement.project_id,
        requirement_id=requirement.id,
        kind=kind,
        title=f"{title_prefix} placeholder for {requirement.key}: {requirement.title}",
        status="Open",
        severity="Medium",
    )
