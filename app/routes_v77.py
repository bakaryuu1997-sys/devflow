from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_calendar_service import prevention_calendar_view, release_readiness_timeline

router = APIRouter(prefix="/api", tags=["v7-7-prevention-calendar"])


@router.get("/projects/{project_id}/prevention-calendar-view")
def api_prevention_calendar_view(project_id: int, db: Session = Depends(get_db)):
    return prevention_calendar_view(db, project_id)


@router.get("/projects/{project_id}/release-readiness-timeline")
def api_release_readiness_timeline(project_id: int, db: Session = Depends(get_db)):
    return release_readiness_timeline(db, project_id)
