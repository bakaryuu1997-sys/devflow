from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.evidence_manifest_service import (
    current_evidence_manifest,
    export_bundle_integrity_check,
    freeze_evidence_manifest,
    list_evidence_manifests,
)

router = APIRouter(prefix="/api", tags=["v8-9-evidence-integrity"])


@router.get("/release-governance/evidence-manifest")
def api_current_evidence_manifest(db: Session = Depends(get_db)):
    return current_evidence_manifest(db)


@router.post("/release-governance/evidence-manifests")
def api_freeze_evidence_manifest(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return freeze_evidence_manifest(db, payload)


@router.get("/release-governance/evidence-manifests")
def api_list_evidence_manifests(db: Session = Depends(get_db)):
    return list_evidence_manifests(db)


@router.get("/release-governance/export-bundle-integrity-check")
def api_export_bundle_integrity_check(db: Session = Depends(get_db)):
    return export_bundle_integrity_check(db)
