from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.tutorial_mode_service import (
    v10_3_demo_data_profiles,
    v10_3_demo_profile_reset_plan,
    v10_3_operator_tutorial_package,
    v10_3_tutorial_progress,
    v10_3_update_tutorial_step,
)

router = APIRouter(prefix="/api", tags=["v10-3-tutorial-mode"])


@router.get("/release-governance/v10-3-demo-data-profiles")
def api_v10_3_demo_data_profiles():
    return v10_3_demo_data_profiles()


@router.get("/release-governance/v10-3-demo-profile-reset-plan")
def api_v10_3_demo_profile_reset_plan(profile_id: str = Query(default="core-risk")):
    return v10_3_demo_profile_reset_plan(profile_id)


@router.get("/release-governance/v10-3-tutorial-progress")
def api_v10_3_tutorial_progress(db: Session = Depends(get_db)):
    return v10_3_tutorial_progress(db)


@router.post("/release-governance/v10-3-tutorial-progress/{step_id}")
def api_v10_3_update_tutorial_step(
    step_id: str,
    status: str = Query(default="Done"),
    operator_name: str = Query(default=""),
    notes: str = Query(default=""),
    db: Session = Depends(get_db),
):
    return v10_3_update_tutorial_step(db, step_id, status, operator_name, notes)


@router.get("/release-governance/v10-3-operator-tutorial-package")
def api_v10_3_operator_tutorial_package(db: Session = Depends(get_db)):
    return v10_3_operator_tutorial_package(db)
