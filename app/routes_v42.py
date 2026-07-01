from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.git_import_service import import_git_items, list_git_items
from app.models import User
from app.openapi_deep_diff_service import deep_openapi_diff
from app.requirement_diff_service import compare_requirement_csv, list_requirement_diffs
from app.schemas import (
    GitImportRequest,
    GitItemRead,
    OpenApiDeepDiffRequest,
    OpenApiDeepFinding,
    RequirementDiffRead,
    RequirementDiffRequest,
    WorkloadRow,
)
from app.workload_service import workload_dashboard

router = APIRouter(prefix="/api/projects/{project_id}", tags=["v4-2-goal-completion"])


@router.post("/git-import", response_model=list[GitItemRead])
def git_import(
    project_id: int, payload: GitImportRequest, db: Session = Depends(get_db), _user: User = Depends(require_write)
):
    return import_git_items(db, project_id, payload.content, payload.item_type)


@router.get("/git-items", response_model=list[GitItemRead])
def git_items(project_id: int, db: Session = Depends(get_db)):
    return list_git_items(db, project_id)


@router.post("/requirement-diff", response_model=list[RequirementDiffRead])
def requirement_diff(
    project_id: int,
    payload: RequirementDiffRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_write),
):
    return compare_requirement_csv(db, project_id, payload.old_csv, payload.new_csv)


@router.get("/requirement-diffs", response_model=list[RequirementDiffRead])
def requirement_diffs(project_id: int, db: Session = Depends(get_db)):
    return list_requirement_diffs(db, project_id)


@router.post("/openapi-deep-diff", response_model=list[OpenApiDeepFinding])
def openapi_deep(project_id: int, payload: OpenApiDeepDiffRequest, _user: User = Depends(require_write)):
    return deep_openapi_diff(payload.before, payload.after)


@router.get("/workload", response_model=list[WorkloadRow])
def workload(project_id: int, db: Session = Depends(get_db)):
    return workload_dashboard(db, project_id)
