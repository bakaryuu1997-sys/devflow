from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.verified_gate_hardening_service import verified_evidence_manifest_gate

router = APIRouter(prefix="/api", tags=["v9-6-verified-evidence-gate"])


@router.get("/release-governance/verified-evidence-manifest-gate")
def api_verified_evidence_manifest_gate(db: Session = Depends(get_db)):
    return verified_evidence_manifest_gate(db)
