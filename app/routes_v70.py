from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ReleaseSignOff
from app.release_snapshot_service import release_snapshot_analytics, snapshot_from_signoff

router = APIRouter(prefix="/api", tags=["v7-0-structured-snapshots"])


@router.get("/release-signoffs/{signoff_id}/structured-snapshot")
def api_release_signoff_structured_snapshot(signoff_id: int, db: Session = Depends(get_db)):
    signoff = db.get(ReleaseSignOff, signoff_id)
    if not signoff:
        raise HTTPException(404, "Release sign-off record not found")
    return {
        "signoff_id": signoff.id,
        "project_id": signoff.project_id,
        "release_version": signoff.release_version,
        "has_structured_snapshot": bool(signoff.snapshot_json),
        "structured_snapshot": snapshot_from_signoff(signoff),
    }


@router.get("/projects/{project_id}/release-snapshot-analytics")
def api_release_snapshot_analytics(project_id: int, db: Session = Depends(get_db)):
    return release_snapshot_analytics(db, project_id)
