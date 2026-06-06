from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.profile_restore_conflict_service import (
    v10_9_execute_guarded_manual_restore,
    v10_9_guarded_restore_plan,
    v10_9_operator_restore_conflict_package,
    v10_9_restore_conflict_report,
    v10_9_restore_digest_lock_audit_trail,
)

router = APIRouter(prefix="/api", tags=["v10-9-restore-conflict-digest-lock"])


@router.get("/release-governance/v10-9-restore-conflict-report")
def api_v10_9_restore_conflict_report(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_9_restore_conflict_report(db, profile_id)


@router.post("/release-governance/v10-9-restore-conflict-report")
def api_v10_9_restore_conflict_report_from_payload(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v10_9_restore_conflict_report(db, profile_id, snapshot_export)


@router.post("/release-governance/v10-9-guarded-restore-plan")
def api_v10_9_guarded_restore_plan(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v10_9_guarded_restore_plan(db, profile_id, snapshot_export)


@router.post("/release-governance/v10-9-execute-guarded-manual-restore")
def api_v10_9_execute_guarded_manual_restore(
    profile_id: str = Query(default="core-risk"),
    restore_approval: str = Query(default=""),
    operator_name: str = Query(default=""),
    snapshot_digest_lock: str = Query(default=""),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v10_9_execute_guarded_manual_restore(db, profile_id, restore_approval, operator_name, snapshot_digest_lock, snapshot_export)


@router.get("/release-governance/v10-9-restore-digest-lock-audit-trail")
def api_v10_9_restore_digest_lock_audit_trail(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_9_restore_digest_lock_audit_trail(db, profile_id)


@router.get("/release-governance/v10-9-operator-restore-conflict-package")
def api_v10_9_operator_restore_conflict_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_9_operator_restore_conflict_package(db, profile_id)
