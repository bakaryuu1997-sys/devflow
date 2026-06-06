from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_release
from app.release_history_service import (
    compare_release_signoffs,
    create_retrospective_note,
    export_retrospective_note,
    list_retrospective_notes,
)
from app.schemas_core import ReleaseRetrospectiveCreate

router = APIRouter(prefix="/api", tags=["v6-8-release-history-retrospective"])


@router.get("/projects/{project_id}/release-signoffs/compare")
def api_compare_release_signoffs(
    project_id: int,
    base_id: int | None = None,
    target_id: int | None = None,
    db: Session = Depends(get_db),
):
    return compare_release_signoffs(db, project_id, base_id, target_id)


@router.get("/projects/{project_id}/release-retrospectives")
def api_release_retrospectives(project_id: int, db: Session = Depends(get_db)):
    return list_retrospective_notes(db, project_id)


@router.post("/projects/{project_id}/release-retrospectives")
def api_create_release_retrospective(
    project_id: int,
    payload: ReleaseRetrospectiveCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_release),
):
    return create_retrospective_note(
        db,
        project_id,
        payload.signoff_id,
        payload.author,
        payload.what_went_well,
        payload.what_to_improve,
        payload.action_items,
    )


@router.get("/release-retrospectives/{note_id}/export")
def api_export_release_retrospective(note_id: int, db: Session = Depends(get_db)):
    note = export_retrospective_note(db, note_id)
    if not note:
        raise HTTPException(404, "Retrospective note not found")
    return note
