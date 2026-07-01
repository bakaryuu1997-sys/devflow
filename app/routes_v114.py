from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.recovery_evidence_handoff_service import (
    v11_4_final_demo_handoff_polish,
    v11_4_operator_demo_handoff_package,
    v11_4_recovery_evidence_bundle,
)

router = APIRouter(prefix="/api", tags=["v11-4-recovery-evidence-handoff"])


@router.get("/release-governance/v11-4-recovery-evidence-bundle")
def api_v11_4_recovery_evidence_bundle(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_4_recovery_evidence_bundle(db, profile_id)


@router.get("/release-governance/v11-4-final-demo-handoff-polish")
def api_v11_4_final_demo_handoff_polish(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_4_final_demo_handoff_polish(db, profile_id)


@router.get("/release-governance/v11-4-operator-demo-handoff-package")
def api_v11_4_operator_demo_handoff_package(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_4_operator_demo_handoff_package(db, profile_id)
