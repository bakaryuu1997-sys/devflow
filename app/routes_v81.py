from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.migration_checker_service import local_database_migration_check, upgrade_safety_report

router = APIRouter(prefix="/api", tags=["v8-1-migration-safety"])


@router.get("/release-governance/local-migration-check")
def api_local_migration_check(db: Session = Depends(get_db)):
    return local_database_migration_check(db)


@router.get("/release-governance/upgrade-safety-report")
def api_upgrade_safety_report(db: Session = Depends(get_db)):
    return upgrade_safety_report(db)
