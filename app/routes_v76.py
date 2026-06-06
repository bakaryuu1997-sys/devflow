from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_prevention_analytics_service import owner_workload_balance, prevention_burndown_analytics

router = APIRouter(prefix="/api", tags=["v7-6-prevention-analytics"])


@router.get("/projects/{project_id}/prevention-burndown-analytics")
def api_prevention_burndown_analytics(project_id: int, db: Session = Depends(get_db)):
    return prevention_burndown_analytics(db, project_id)


@router.get("/projects/{project_id}/owner-workload-balance")
def api_owner_workload_balance(project_id: int, db: Session = Depends(get_db)):
    return owner_workload_balance(db, project_id)
