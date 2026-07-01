from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.advanced_readiness_service import advanced_readiness
from app.bug_pattern_service import bug_pattern_dashboard
from app.code_risk_service import analyze_code_changes, list_code_changes
from app.database import get_db
from app.deps import require_write
from app.env_guard_service import analyze_env
from app.impact_service import analyze_impact, list_requirement_changes, record_requirement_change
from app.models import User
from app.schemas import (
    AdvancedReadinessRead,
    BugPatternRow,
    CodeChangeAnalyzeRequest,
    CodeChangeRead,
    EnvFinding,
    EnvGuardRequest,
    ImpactAnalysisRead,
    RequirementChangeCreate,
    RequirementChangeRead,
    TraceabilityRow,
    TraceLinkCreate,
    TraceLinkRead,
)
from app.traceability_service import create_trace_link, list_trace_links, traceability_matrix

router = APIRouter(prefix="/api/projects/{project_id}", tags=["v4-risk-control"])


@router.post("/trace-links", response_model=TraceLinkRead)
def add_trace_link(
    project_id: int, payload: TraceLinkCreate, db: Session = Depends(get_db), _user: User = Depends(require_write)
):
    return create_trace_link(db, project_id, payload)


@router.get("/trace-links", response_model=list[TraceLinkRead])
def trace_links(project_id: int, db: Session = Depends(get_db)):
    return list_trace_links(db, project_id)


@router.get("/traceability", response_model=list[TraceabilityRow])
def traceability(project_id: int, db: Session = Depends(get_db)):
    return traceability_matrix(db, project_id)


@router.post("/requirement-changes", response_model=RequirementChangeRead)
def add_requirement_change(
    project_id: int,
    payload: RequirementChangeCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_write),
):
    return record_requirement_change(db, project_id, payload)


@router.get("/requirement-changes", response_model=list[RequirementChangeRead])
def requirement_changes(project_id: int, db: Session = Depends(get_db)):
    return list_requirement_changes(db, project_id)


@router.get("/impact/{requirement_key}", response_model=ImpactAnalysisRead)
def impact(project_id: int, requirement_key: str, db: Session = Depends(get_db)):
    return analyze_impact(db, project_id, requirement_key)


@router.post("/code-risk", response_model=list[CodeChangeRead])
def code_risk(
    project_id: int,
    payload: CodeChangeAnalyzeRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_write),
):
    return analyze_code_changes(db, project_id, payload)


@router.get("/code-risk", response_model=list[CodeChangeRead])
def code_risk_list(project_id: int, db: Session = Depends(get_db)):
    return list_code_changes(db, project_id)


@router.post("/env-guard", response_model=list[EnvFinding])
def env_guard(project_id: int, payload: EnvGuardRequest, _user: User = Depends(require_write)):
    return analyze_env(payload.content, payload.required_keys)


@router.get("/bug-patterns", response_model=list[BugPatternRow])
def bug_patterns(project_id: int, db: Session = Depends(get_db)):
    return bug_pattern_dashboard(db, project_id)


@router.get("/advanced-readiness", response_model=AdvancedReadinessRead)
def advanced(project_id: int, db: Session = Depends(get_db)):
    return advanced_readiness(db, project_id)
