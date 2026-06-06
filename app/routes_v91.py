from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.signature_import_service import (
    attach_timestamp_token_evidence,
    create_signed_payload_verification,
    list_signed_payload_verifications,
    list_timestamp_token_evidence,
    signed_payload_import_package,
    signed_payload_timestamp_integrity_check,
    timestamp_token_evidence_package,
)

router = APIRouter(prefix="/api", tags=["v9-1-signed-payload-import"])


@router.get("/release-governance/signed-payload-import-package")
def api_signed_payload_import_package(db: Session = Depends(get_db)):
    return signed_payload_import_package(db)


@router.post("/release-governance/signed-payload-verifications")
def api_create_signed_payload_verification(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return create_signed_payload_verification(db, payload)


@router.get("/release-governance/signed-payload-verifications")
def api_list_signed_payload_verifications(db: Session = Depends(get_db)):
    return list_signed_payload_verifications(db)


@router.get("/release-governance/timestamp-token-evidence-package")
def api_timestamp_token_evidence_package(db: Session = Depends(get_db)):
    return timestamp_token_evidence_package(db)


@router.post("/release-governance/timestamp-token-evidence-attachments")
def api_attach_timestamp_token_evidence(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return attach_timestamp_token_evidence(db, payload)


@router.get("/release-governance/timestamp-token-evidence-attachments")
def api_list_timestamp_token_evidence(db: Session = Depends(get_db)):
    return list_timestamp_token_evidence(db)


@router.get("/release-governance/signed-payload-timestamp-integrity-check")
def api_signed_payload_timestamp_integrity_check(db: Session = Depends(get_db)):
    return signed_payload_timestamp_integrity_check(db)
