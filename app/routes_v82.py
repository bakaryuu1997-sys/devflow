from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.migration_sql_service import backup_checklist, dry_run_sql_migration

router = APIRouter(prefix="/api", tags=["v8-2-dry-run-migration"])


@router.get("/release-governance/dry-run-sql-migration")
def api_dry_run_sql_migration(db: Session = Depends(get_db)):
    return dry_run_sql_migration(db)


@router.get("/release-governance/backup-checklist")
def api_backup_checklist(db: Session = Depends(get_db)):
    return backup_checklist(db)
