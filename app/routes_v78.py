from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_release
from app.release_scenario_service import adjust_prevention_scope, release_readiness_scenarios

router = APIRouter(prefix="/api", tags=["v7-8-release-scenarios"])


class ScopeAdjustmentRequest(BaseModel):
    status: str = "Open"
    owner: str = ""
    due_date: str = ""
    reason: str = ""


@router.get("/projects/{project_id}/release-readiness-scenarios")
def api_release_readiness_scenarios(project_id: int, target_days: int = 14, db: Session = Depends(get_db)):
    return release_readiness_scenarios(db, project_id, target_days)


@router.post("/release-learning-items/{item_id}/scope-adjustment")
def api_adjust_prevention_scope(
    item_id: int,
    payload: ScopeAdjustmentRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_release),
):
    result = adjust_prevention_scope(db, item_id, payload.status, payload.owner, payload.due_date, payload.reason)
    if not result:
        raise HTTPException(404, "Release learning item not found")
    return result
