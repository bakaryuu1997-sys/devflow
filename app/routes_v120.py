from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.production_deployment_checklist_service import (
    v12_0_baseline_freeze_summary,
    v12_0_operator_deployment_package,
    v12_0_production_deployment_checklist,
)

router = APIRouter(prefix="/api", tags=["v12-0-production-deployment-checklist"])


@router.get("/release-governance/v12-0-baseline-freeze-summary")
def api_v12_0_baseline_freeze_summary(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v12_0_baseline_freeze_summary(db, profile_id)


@router.get("/release-governance/v12-0-production-deployment-checklist")
def api_v12_0_production_deployment_checklist(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v12_0_production_deployment_checklist(db, profile_id)


@router.get("/release-governance/v12-0-operator-deployment-package")
def api_v12_0_operator_deployment_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v12_0_operator_deployment_package(db, profile_id)
