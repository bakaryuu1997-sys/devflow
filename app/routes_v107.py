from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.profile_rollback_rehearsal_service import (
    v10_7_manual_rollback_import_rehearsal,
    v10_7_operator_restore_package,
    v10_7_restore_checklist,
)

router = APIRouter(prefix="/api", tags=["v10-7-manual-rollback-rehearsal"])


@router.get("/release-governance/v10-7-manual-rollback-import-rehearsal")
def api_v10_7_manual_rollback_import_rehearsal(
    profile_id: str = Query(default="core-risk"),
    db: Session = Depends(get_db),
):
    return v10_7_manual_rollback_import_rehearsal(db, profile_id)


@router.post("/release-governance/v10-7-manual-rollback-import-rehearsal")
def api_v10_7_manual_rollback_import_rehearsal_from_payload(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v10_7_manual_rollback_import_rehearsal(db, profile_id, snapshot_export)


@router.get("/release-governance/v10-7-restore-checklist")
def api_v10_7_restore_checklist(profile_id: str = Query(default="core-risk")):
    return v10_7_restore_checklist(profile_id)


@router.get("/release-governance/v10-7-operator-restore-package")
def api_v10_7_operator_restore_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v10_7_operator_restore_package(db, profile_id)
