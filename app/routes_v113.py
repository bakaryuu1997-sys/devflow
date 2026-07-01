from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.recovery_smoke_verification_service import (
    v11_3_operator_smoke_verification_package,
    v11_3_post_restore_verification_report,
    v11_3_recovery_smoke_test_automation,
)

router = APIRouter(prefix="/api", tags=["v11-3-recovery-smoke-verification"])


@router.get("/release-governance/v11-3-recovery-smoke-test-automation")
def api_v11_3_recovery_smoke_test_automation(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_3_recovery_smoke_test_automation(db, profile_id)


@router.post("/release-governance/v11-3-post-restore-verification-report")
def api_v11_3_post_restore_verification_report(
    profile_id: str = Query(default="core-risk"),
    snapshot_export: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v11_3_post_restore_verification_report(db, profile_id, snapshot_export)


@router.get("/release-governance/v11-3-operator-smoke-verification-package")
def api_v11_3_operator_smoke_verification_package(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_3_operator_smoke_verification_package(db, profile_id)
