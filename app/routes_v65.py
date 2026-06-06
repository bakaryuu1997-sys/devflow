from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.models import WorkItem
from app.release_review_checklist_service import release_review_checklist
from app.schemas import WorkItemConvertPlaceholder, WorkItemRead

router = APIRouter(prefix="/api", tags=["v6-5-release-review"])


@router.post("/work-items/{item_id}/convert-placeholder", response_model=WorkItemRead)
def api_convert_placeholder(
    item_id: int,
    payload: WorkItemConvertPlaceholder,
    db: Session = Depends(get_db),
    _user=Depends(require_write),
):
    item = db.get(WorkItem, item_id)
    if not item:
        raise HTTPException(404, "Work item not found")
    if not _is_placeholder(item):
        raise HTTPException(400, "Only placeholder work items can be converted")
    title = payload.title.strip()
    if not title:
        raise HTTPException(400, "Converted work item title is required")
    item.title = title
    item.status = payload.status
    item.severity = payload.severity
    db.commit()
    db.refresh(item)
    return item


@router.get("/projects/{project_id}/release-review-checklist")
def api_release_review_checklist(project_id: int, db: Session = Depends(get_db)):
    return release_review_checklist(db, project_id)


def _is_placeholder(item: WorkItem) -> bool:
    title = item.title.lower()
    return "placeholder for" in title or title.startswith("implementation task placeholder") or title.startswith("test coverage placeholder")
