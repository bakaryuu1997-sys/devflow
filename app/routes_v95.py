from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.public_verifier_evidence_service import (
    attach_public_verifier_evidence,
    list_public_verifier_evidence,
    public_verifier_evidence_package,
    verified_signature_approval_gate,
)

router = APIRouter(prefix="/api", tags=["v9-5-public-verifier-evidence"])


@router.get("/release-governance/public-verifier-evidence-package")
def api_public_verifier_evidence_package(db: Session = Depends(get_db)):
    return public_verifier_evidence_package(db)


@router.post("/release-governance/public-verifier-evidence-attachments")
def api_attach_public_verifier_evidence(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return attach_public_verifier_evidence(db, payload)


@router.get("/release-governance/public-verifier-evidence-attachments")
def api_list_public_verifier_evidence(db: Session = Depends(get_db)):
    return list_public_verifier_evidence(db)


@router.get("/release-governance/verified-signature-approval-gate")
def api_verified_signature_approval_gate(db: Session = Depends(get_db)):
    return verified_signature_approval_gate(db)
