from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.crypto_signing_service import (
    create_timestamp_handoff,
    cryptographic_signing_readiness,
    external_timestamp_handoff_package,
    list_timestamp_handoffs,
    timestamp_handoff_integrity_check,
)
from app.database import get_db

router = APIRouter(prefix="/api", tags=["v9-0-crypto-signing-readiness"])


@router.get("/release-governance/cryptographic-signing-readiness")
def api_cryptographic_signing_readiness(db: Session = Depends(get_db)):
    return cryptographic_signing_readiness(db)


@router.get("/release-governance/external-timestamp-handoff-package")
def api_external_timestamp_handoff_package(db: Session = Depends(get_db)):
    return external_timestamp_handoff_package(db)


@router.post("/release-governance/external-timestamp-handoffs")
def api_create_timestamp_handoff(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return create_timestamp_handoff(db, payload)


@router.get("/release-governance/external-timestamp-handoffs")
def api_list_timestamp_handoffs(db: Session = Depends(get_db)):
    return list_timestamp_handoffs(db)


@router.get("/release-governance/timestamp-handoff-integrity-check")
def api_timestamp_handoff_integrity_check(db: Session = Depends(get_db)):
    return timestamp_handoff_integrity_check(db)
