from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_plan_recommendation_service import release_plan_recommendation
from app.release_scenario_service import scope_decision_audit_trail

router = APIRouter(prefix="/api", tags=["v7-9-release-plan-recommendations"])


@router.get("/projects/{project_id}/release-plan-recommendation")
def api_release_plan_recommendation(project_id: int, target_days: int = 14, db: Session = Depends(get_db)):
    return release_plan_recommendation(db, project_id, target_days)


@router.get("/projects/{project_id}/scope-decision-audit")
def api_scope_decision_audit(project_id: int, limit: int = 50, db: Session = Depends(get_db)):
    return scope_decision_audit_trail(db, project_id, limit)
