from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_recurring_risk_service import recurring_risk_trends

router = APIRouter(prefix="/api", tags=["v7-2-recurring-risk-trends"])


@router.get("/projects/{project_id}/recurring-risk-trends")
def api_recurring_risk_trends(
    project_id: int,
    limit: int = Query(default=5, ge=2, le=20),
    db: Session = Depends(get_db),
):
    return recurring_risk_trends(db, project_id, limit)
