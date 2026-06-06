from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_risk_delta_service import release_risk_delta

router = APIRouter(prefix="/api", tags=["v7-1-risk-delta-analytics"])


@router.get("/projects/{project_id}/release-risk-delta")
def api_release_risk_delta(
    project_id: int,
    base_id: int | None = Query(default=None),
    target_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return release_risk_delta(db, project_id, base_id, target_id)
