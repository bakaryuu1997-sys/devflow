from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.signature_policy_service import (
    policy_based_verification_checklist,
    signature_adapter_dry_run,
    signature_verification_adapter_stubs,
)

router = APIRouter(prefix="/api", tags=["v9-2-signature-policy-adapters"])


@router.get("/release-governance/signature-verification-adapter-stubs")
def api_signature_verification_adapter_stubs(db: Session = Depends(get_db)):
    return signature_verification_adapter_stubs(db)


@router.get("/release-governance/policy-based-verification-checklist")
def api_policy_based_verification_checklist(db: Session = Depends(get_db)):
    return policy_based_verification_checklist(db)


@router.post("/release-governance/signature-adapter-dry-run")
def api_signature_adapter_dry_run(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return signature_adapter_dry_run(db, payload)
