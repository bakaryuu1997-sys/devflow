from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_governance_service import governance_readiness, migration_notes

router = APIRouter(prefix="/api", tags=["v8-0-release-governance"])


@router.get("/projects/{project_id}/release-governance-readiness")
def api_release_governance_readiness(project_id: int, target_days: int = 14, db: Session = Depends(get_db)):
    return governance_readiness(db, project_id, target_days)


@router.get("/release-governance/migration-notes")
def api_release_governance_migration_notes():
    return migration_notes()
