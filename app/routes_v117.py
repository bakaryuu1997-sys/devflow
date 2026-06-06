from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.archive_integrity_service import (
    v11_7_archive_integrity_manifest,
    v11_7_operator_release_package,
    v11_7_release_notes_polish,
)
from app.database import get_db

router = APIRouter(prefix="/api", tags=["v11-7-archive-integrity-release-notes"])


@router.get("/release-governance/v11-7-archive-integrity-manifest")
def api_v11_7_archive_integrity_manifest(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_7_archive_integrity_manifest(db, profile_id)


@router.get("/release-governance/v11-7-release-notes-polish")
def api_v11_7_release_notes_polish(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_7_release_notes_polish(db, profile_id)


@router.get("/release-governance/v11-7-operator-release-package")
def api_v11_7_operator_release_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_7_operator_release_package(db, profile_id)
