from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_release
from app.release_signoff_service import (
    approval_record,
    create_release_signoff,
    list_release_signoffs,
    release_signoff_snapshot,
)
from app.schemas_core import ReleaseSignOffCreate

router = APIRouter(prefix="/api", tags=["v6-7-release-signoff"])


@router.get("/projects/{project_id}/release-signoff-snapshot")
def api_release_signoff_snapshot(project_id: int, db: Session = Depends(get_db)):
    return release_signoff_snapshot(db, project_id)


@router.get("/projects/{project_id}/release-signoffs")
def api_release_signoffs(project_id: int, db: Session = Depends(get_db)):
    return list_release_signoffs(db, project_id)


@router.post("/projects/{project_id}/release-signoffs")
def api_create_release_signoff(
    project_id: int,
    payload: ReleaseSignOffCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_release),
):
    return create_release_signoff(db, project_id, payload.approved_by, payload.approval_note)


@router.get("/release-signoffs/{signoff_id}/approval-record")
def api_release_signoff_approval_record(signoff_id: int, db: Session = Depends(get_db)):
    record = approval_record(db, signoff_id)
    if not record:
        raise HTTPException(404, "Release sign-off record not found")
    return record
