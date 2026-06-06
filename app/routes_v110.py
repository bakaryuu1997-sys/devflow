from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.restore_governance_stabilization_service import (
    v11_0_final_operator_recovery_runbook,
    v11_0_operator_recovery_package,
    v11_0_restore_governance_stability_report,
)

router = APIRouter(prefix="/api", tags=["v11-0-restore-governance-stabilization"])


@router.post("/release-governance/v11-0-restore-governance-stability-report")
def api_v11_0_restore_governance_stability_report(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v11_0_restore_governance_stability_report(db, profile_id, snapshot_export)


@router.post("/release-governance/v11-0-final-operator-recovery-runbook")
def api_v11_0_final_operator_recovery_runbook(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v11_0_final_operator_recovery_runbook(db, profile_id, snapshot_export)


@router.get("/release-governance/v11-0-operator-recovery-package")
def api_v11_0_operator_recovery_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_0_operator_recovery_package(db, profile_id)
