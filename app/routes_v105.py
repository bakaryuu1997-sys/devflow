from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.profile_reset_orchestrator_service import (
    v10_5_execute_profile_reset,
    v10_5_operator_reset_package,
    v10_5_profile_reset_plan,
)

router = APIRouter(prefix="/api", tags=["v10-5-profile-reset-orchestrator"])


@router.get("/release-governance/v10-5-profile-reset-plan")
def api_v10_5_profile_reset_plan(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_5_profile_reset_plan(db, profile_id)


@router.post("/release-governance/v10-5-execute-profile-reset")
def api_v10_5_execute_profile_reset(
    profile_id: str = Query(default="core-risk"),
    approval: str = Query(default=""),
    operator_name: str = Query(default=""),
    db: Session = Depends(get_db),
):
    return v10_5_execute_profile_reset(db, profile_id, approval, operator_name)


@router.get("/release-governance/v10-5-operator-reset-package")
def api_v10_5_operator_reset_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_5_operator_reset_package(db, profile_id)
