from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.release_prevention_backlog_service import auto_create_learning_items_from_backlog, risk_prevention_backlog

router = APIRouter(prefix="/api", tags=["v7-3-risk-prevention-backlog"])


@router.get("/projects/{project_id}/risk-prevention-backlog")
def api_risk_prevention_backlog(
    project_id: int,
    limit: int = Query(default=5, ge=2, le=20),
    db: Session = Depends(get_db),
):
    return risk_prevention_backlog(db, project_id, limit)


@router.post("/projects/{project_id}/risk-prevention-backlog/auto-create")
def api_auto_create_risk_prevention_items(
    project_id: int,
    limit: int = Query(default=5, ge=2, le=20),
    db: Session = Depends(get_db),
    _user=Depends(require_write),
):
    return auto_create_learning_items_from_backlog(db, project_id, limit)
