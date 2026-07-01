from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.profile_manual_restore_service import (
    v10_8_execute_guarded_manual_restore,
    v10_8_guarded_restore_plan,
    v10_8_operator_restore_execution_package,
    v10_8_restore_audit_trail,
)

router = APIRouter(prefix="/api", tags=["v10-8-guarded-manual-restore"])


@router.get("/release-governance/v10-8-guarded-restore-plan")
def api_v10_8_guarded_restore_plan(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_8_guarded_restore_plan(db, profile_id)


@router.post("/release-governance/v10-8-guarded-restore-plan")
def api_v10_8_guarded_restore_plan_from_payload(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v10_8_guarded_restore_plan(db, profile_id, snapshot_export)


@router.post("/release-governance/v10-8-execute-guarded-manual-restore")
def api_v10_8_execute_guarded_manual_restore(
    profile_id: str = Query(default="core-risk"),
    restore_approval: str = Query(default=""),
    operator_name: str = Query(default=""),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v10_8_execute_guarded_manual_restore(db, profile_id, restore_approval, operator_name, snapshot_export)


@router.get("/release-governance/v10-8-restore-audit-trail")
def api_v10_8_restore_audit_trail(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_8_restore_audit_trail(db, profile_id)


@router.get("/release-governance/v10-8-operator-restore-execution-package")
def api_v10_8_operator_restore_execution_package(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v10_8_operator_restore_execution_package(db, profile_id)
