from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.profile_reset_snapshot_service import (
    v10_6_execute_profile_reset_with_audit,
    v10_6_operator_rollback_package,
    v10_6_profile_reset_audit_trail,
    v10_6_rollback_snapshot_export,
)

router = APIRouter(prefix="/api", tags=["v10-6-profile-reset-audit"])


@router.get("/release-governance/v10-6-rollback-snapshot")
def api_v10_6_rollback_snapshot(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_6_rollback_snapshot_export(db, profile_id)


@router.post("/release-governance/v10-6-execute-profile-reset")
def api_v10_6_execute_profile_reset(
    profile_id: str = Query(default="core-risk"),
    approval: str = Query(default=""),
    operator_name: str = Query(default=""),
    db: Session = Depends(get_db),
):
    return v10_6_execute_profile_reset_with_audit(db, profile_id, approval, operator_name)


@router.get("/release-governance/v10-6-profile-reset-audit-trail")
def api_v10_6_profile_reset_audit_trail(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_6_profile_reset_audit_trail(db, profile_id)


@router.get("/release-governance/v10-6-operator-rollback-package")
def api_v10_6_operator_rollback_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_6_operator_rollback_package(db, profile_id)
