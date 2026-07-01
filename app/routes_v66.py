from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.models import Requirement
from app.release_completion_service import (
    mark_requirement_review_complete,
    project_release_review_completion,
    reopen_requirement_review,
    requirement_done_gates,
)

router = APIRouter(prefix="/api", tags=["v6-6-release-completion"])


@router.get("/projects/{project_id}/release-review-completion")
def api_release_review_completion(project_id: int, db: Session = Depends(get_db)):
    return project_release_review_completion(db, project_id)


@router.get("/requirements/{requirement_id}/done-gates")
def api_requirement_done_gates(requirement_id: int, db: Session = Depends(get_db)):
    requirement = _requirement_or_404(db, requirement_id)
    return requirement_done_gates(db, requirement)


@router.post("/requirements/{requirement_id}/review-complete")
def api_mark_requirement_review_complete(
    requirement_id: int, db: Session = Depends(get_db), _user=Depends(require_write)
):
    requirement = _requirement_or_404(db, requirement_id)
    if requirement.status == "Archived":
        raise HTTPException(400, "Archived requirements cannot be marked review complete")
    return mark_requirement_review_complete(db, requirement)


@router.post("/requirements/{requirement_id}/review-reopen")
def api_reopen_requirement_review(requirement_id: int, db: Session = Depends(get_db), _user=Depends(require_write)):
    requirement = _requirement_or_404(db, requirement_id)
    return reopen_requirement_review(db, requirement)


def _requirement_or_404(db: Session, requirement_id: int) -> Requirement:
    requirement = db.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")
    return requirement
