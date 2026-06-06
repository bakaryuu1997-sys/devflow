from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_next_readiness_service import next_release_readiness

router = APIRouter(prefix="/api", tags=["v7-4-next-release-readiness"])


@router.get("/projects/{project_id}/next-release-readiness")
def api_next_release_readiness(project_id: int, db: Session = Depends(get_db)):
    return next_release_readiness(db, project_id)
