from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.final_evidence_bundle_service import create_final_signed_release_bundle, final_signed_release_bundle_package, list_final_signed_release_bundles

router = APIRouter(prefix="/api", tags=["v9-8-final-evidence-bundle"])


@router.get("/release-governance/final-signed-evidence-bundle")
def api_final_signed_release_bundle_package(db: Session = Depends(get_db)):
    return final_signed_release_bundle_package(db)


@router.post("/release-governance/final-signed-evidence-bundles")
def api_create_final_signed_release_bundle(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return create_final_signed_release_bundle(db, payload)


@router.get("/release-governance/final-signed-evidence-bundles")
def api_list_final_signed_release_bundles(db: Session = Depends(get_db)):
    return list_final_signed_release_bundles(db)
