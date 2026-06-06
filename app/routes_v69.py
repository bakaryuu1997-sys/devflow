from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_release, require_write
from app.release_learning_service import create_learning_item, release_learning_loop, update_learning_item_planning, update_learning_item_status
from app.schemas_core import ReleaseLearningItemCreate, ReleaseLearningItemPlanningUpdate, ReleaseLearningItemStatusUpdate

router = APIRouter(prefix="/api", tags=["v6-9-release-learning-loop"])


@router.get("/projects/{project_id}/release-learning-loop")
def api_release_learning_loop(project_id: int, db: Session = Depends(get_db)):
    return release_learning_loop(db, project_id)


@router.post("/projects/{project_id}/release-learning-items")
def api_create_release_learning_item(
    project_id: int,
    payload: ReleaseLearningItemCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_write),
):
    return create_learning_item(
        db,
        project_id,
        payload.title,
        payload.prevention_action,
        payload.source,
        payload.status,
        payload.owner,
        payload.due_date,
    )


@router.patch("/release-learning-items/{item_id}")
def api_update_release_learning_item_status(
    item_id: int,
    payload: ReleaseLearningItemStatusUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_release),
):
    result = update_learning_item_status(db, item_id, payload.status)
    if not result:
        raise HTTPException(404, "Release learning item not found")
    return result


@router.patch("/release-learning-items/{item_id}/planning")
def api_update_release_learning_item_planning(
    item_id: int,
    payload: ReleaseLearningItemPlanningUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_release),
):
    result = update_learning_item_planning(db, item_id, payload.owner, payload.due_date, payload.status)
    if not result:
        raise HTTPException(404, "Release learning item not found")
    return result
