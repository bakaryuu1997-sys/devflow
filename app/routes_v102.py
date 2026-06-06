from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.first_run_wizard_service import (
    v10_2_demo_reset_plan,
    v10_2_demo_reset_safety_check,
    v10_2_first_run_wizard,
    v10_2_operator_first_run_package,
)

router = APIRouter(prefix="/api", tags=["v10-2-first-run-wizard"])


@router.get("/release-governance/v10-2-first-run-wizard")
def api_v10_2_first_run_wizard(db: Session = Depends(get_db)):
    return v10_2_first_run_wizard(db)


@router.get("/release-governance/v10-2-demo-reset-safety-check")
def api_v10_2_demo_reset_safety_check(db: Session = Depends(get_db)):
    return v10_2_demo_reset_safety_check(db)


@router.get("/release-governance/v10-2-demo-reset-plan")
def api_v10_2_demo_reset_plan(db: Session = Depends(get_db)):
    return v10_2_demo_reset_plan(db)


@router.get("/release-governance/v10-2-operator-first-run-package")
def api_v10_2_operator_first_run_package(db: Session = Depends(get_db)):
    return v10_2_operator_first_run_package(db)
