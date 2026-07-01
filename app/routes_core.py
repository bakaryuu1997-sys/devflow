from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_mode import is_production_mode
from app.auth_service import create_user
from app.config import settings
from app.database import Base, engine, get_db
from app.deps import require_release, require_write
from app.models import ActivityLog, Project, Release, Requirement, TraceLink, WorkItem
from app.release_risk_dashboard_service import release_risk_dashboard
from app.schemas import (
    ProjectCreate,
    ProjectRead,
    ReleaseCreate,
    ReleaseRead,
    RequirementCreate,
    RequirementRead,
    RequirementUpdate,
    RiskRead,
    WorkItemCreate,
    WorkItemRead,
    WorkItemUpdate,
)
from app.services import calculate_readiness, create_project, dashboard, run_risk_scan

router = APIRouter(prefix="/api", tags=["core"])

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    if is_production_mode() or not settings.allow_demo_reset:
        raise HTTPException(status_code=403, detail="Demo reset is disabled")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    project = create_project(db, "Payroll System", "Demo project for release risk control.")
    create_user(db, "admin@example.com", "password123", "admin")
    req = Requirement(project_id=project.id, key="REQ-001", title="Login by email", priority="Critical")
    db.add(req)
    db.commit()
    db.refresh(req)
    db.add(WorkItem(project_id=project.id, requirement_id=req.id, kind="task", title="Build login API", status="Done"))
    db.add(WorkItem(project_id=project.id, requirement_id=req.id, kind="bug", title="Login returns 500", status="Open", severity="Critical"))
    db.add(TraceLink(project_id=project.id, requirement_key="REQ-001", link_type="api", target_key="POST /api/auth/login", title="Login API", status="Changed", module="auth"))
    db.add(TraceLink(project_id=project.id, requirement_key="REQ-001", link_type="task", target_key="TASK-LOGIN-API", title="Build login API", status="Done", module="auth"))
    db.add(TraceLink(project_id=project.id, requirement_key="REQ-001", link_type="test", target_key="TC-LOGIN-001", title="Login success test", status="Needs Update", module="auth"))
    db.add(TraceLink(project_id=project.id, requirement_key="REQ-001", link_type="bug", target_key="BUG-LOGIN-500", title="Critical login bug", status="Open", module="auth"))
    db.add(TraceLink(project_id=project.id, requirement_key="REQ-001", link_type="commit", target_key="abc123", title="TASK-LOGIN-API update auth flow", status="Merged", module="auth"))
    db.add(Release(project_id=project.id, version="1.0.0"))
    db.commit()
    return {"project_id": project.id, "message": "Demo reset complete"}

@router.post("/demo/fix")
def fix_demo(db: Session = Depends(get_db)):
    bugs = db.scalars(select(WorkItem).where(WorkItem.kind == "bug")).all()
    for bug in bugs:
        bug.status = "Closed"
    req = db.scalars(select(Requirement).where(Requirement.key == "REQ-001")).first()
    if req:
        db.add(WorkItem(project_id=req.project_id, requirement_id=req.id, kind="test", title="Login regression test", status="Done"))
    db.commit()
    return {"message": "Demo blockers fixed"}

@router.post("/projects", response_model=ProjectRead)
def api_create_project(payload: ProjectCreate, db: Session = Depends(get_db), _user=Depends(require_write)):
    return create_project(db, payload.name, payload.description)

@router.get("/projects", response_model=list[ProjectRead])
def api_projects(db: Session = Depends(get_db)):
    return list(db.scalars(select(Project)).all())

@router.get("/projects/{project_id}/dashboard")
def api_dashboard(project_id: int, db: Session = Depends(get_db)):
    return dashboard(db, project_id)

@router.post("/projects/{project_id}/requirements", response_model=RequirementRead)
def api_create_requirement(project_id: int, payload: RequirementCreate, db: Session = Depends(get_db), _user=Depends(require_write)):
    req = Requirement(project_id=project_id, **payload.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.get("/projects/{project_id}/requirements", response_model=list[RequirementRead])
def api_requirements(project_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Requirement).where(Requirement.project_id == project_id)).all())

@router.patch("/requirements/{requirement_id}", response_model=RequirementRead)
def api_update_requirement(requirement_id: int, payload: RequirementUpdate, db: Session = Depends(get_db), _user=Depends(require_write)):
    requirement = db.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if value is not None:
            setattr(requirement, key, value)
    db.commit()
    db.refresh(requirement)
    return requirement

@router.post("/requirements/{requirement_id}/archive", response_model=RequirementRead)
def api_archive_requirement(requirement_id: int, db: Session = Depends(get_db), _user=Depends(require_write)):
    requirement = db.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")
    requirement.status = "Archived"
    db.commit()
    db.refresh(requirement)
    return requirement

@router.post("/projects/{project_id}/work-items", response_model=WorkItemRead)
def api_create_work_item(project_id: int, payload: WorkItemCreate, db: Session = Depends(get_db), _user=Depends(require_write)):
    if payload.requirement_id is not None:
        _require_project_requirement(db, project_id, payload.requirement_id)
    item = WorkItem(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/projects/{project_id}/work-items", response_model=list[WorkItemRead])
def api_work_items(project_id: int, requirement_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = select(WorkItem).where(WorkItem.project_id == project_id)
    if requirement_id is not None:
        stmt = stmt.where(WorkItem.requirement_id == requirement_id)
    return list(db.scalars(stmt).all())

@router.patch("/work-items/{item_id}", response_model=WorkItemRead)
def api_update_work_item(item_id: int, payload: WorkItemUpdate, db: Session = Depends(get_db), _user=Depends(require_write)):
    item = db.get(WorkItem, item_id)
    if not item:
        raise HTTPException(404, "Work item not found")
    data = payload.model_dump(exclude_unset=True)
    if "requirement_id" in data and data["requirement_id"] is not None:
        _require_project_requirement(db, item.project_id, data["requirement_id"])
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

def _require_project_requirement(db: Session, project_id: int, requirement_id: int) -> Requirement:
    requirement = db.get(Requirement, requirement_id)
    if not requirement or requirement.project_id != project_id:
        raise HTTPException(400, "Requirement does not belong to this project")
    return requirement


@router.post("/projects/{project_id}/risks/run", response_model=list[RiskRead])
def api_run_risks(project_id: int, db: Session = Depends(get_db), _user=Depends(require_write)):
    return run_risk_scan(db, project_id)

@router.get("/projects/{project_id}/release-risk-dashboard")
def api_release_risk_dashboard(project_id: int, db: Session = Depends(get_db)):
    return release_risk_dashboard(db, project_id)

@router.get("/projects/{project_id}/risks", response_model=list[RiskRead])
def api_risks(project_id: int, db: Session = Depends(get_db)):
    requirements = list(db.scalars(select(Requirement).where(Requirement.project_id == project_id)).all())
    if not requirements:
        return []
    return run_risk_scan(db, project_id)

@router.post("/projects/{project_id}/releases", response_model=ReleaseRead)
def api_create_release(project_id: int, payload: ReleaseCreate, db: Session = Depends(get_db), _user=Depends(require_release)):
    release = Release(project_id=project_id, version=payload.version)
    db.add(release)
    db.commit()
    db.refresh(release)
    return release

@router.get("/projects/{project_id}/releases", response_model=list[ReleaseRead])
def api_releases(project_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Release).where(Release.project_id == project_id)).all())

@router.post("/releases/{release_id}/readiness")
def api_release_readiness(release_id: int, db: Session = Depends(get_db), _user=Depends(require_release)):
    release = db.get(Release, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    return calculate_readiness(db, release)

@router.get("/releases/{release_id}/notes")
def api_release_notes(release_id: int, db: Session = Depends(get_db)):
    release = db.get(Release, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    return {"content": f"# Release {release.version}\n\nStatus: {release.status}\nScore: {release.readiness_score}\nGate passed: {release.gate_passed}"}

@router.get("/governance/verify-ledger")
def verify_ledger(db: Session = Depends(get_db)):
    from hashlib import sha256
    
    logs = db.scalars(select(ActivityLog).order_by(ActivityLog.id.asc())).all()
    
    expected_prev_hash = "0" * 64
    for log in logs:
        # Check chain continuity
        if log.previous_hash != expected_prev_hash:
            return {
                "status": "tampered",
                "reason": f"Chain link broken at record ID {log.id}. Expected prev_hash '{expected_prev_hash}', got '{log.previous_hash}'",
                "record_id": log.id,
                "expected_previous_hash": expected_prev_hash,
                "actual_previous_hash": log.previous_hash
            }
        
        # Verify content integrity
        created_dt = log.created_at
        if created_dt.tzinfo is not None:
            from datetime import UTC
            created_dt = created_dt.astimezone(UTC).replace(tzinfo=None)
        created_str = str(created_dt)
        project_id_str = str(log.project_id) if log.project_id else "None"
        payload = f"{log.action}:{log.message}:{created_str}:{project_id_str}:{log.previous_hash}"
        calculated_hash = sha256(payload.encode("utf-8")).hexdigest()
        
        if log.current_hash != calculated_hash:
            return {
                "status": "tampered",
                "reason": f"Hash mismatch at record ID {log.id}. Data has been modified.",
                "record_id": log.id,
                "expected_hash": calculated_hash,
                "actual_hash": log.current_hash
            }
        
        expected_prev_hash = log.current_hash
        
    return {
        "status": "verified",
        "count": len(logs)
    }
