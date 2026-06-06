from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.migration_copy_apply_service import rollback_drill_automation_plan, safe_copy_migration_apply_assistant

router = APIRouter(prefix="/api", tags=["v8-4-safe-copy-migration"])


@router.get("/release-governance/safe-copy-migration-apply")
def api_safe_copy_migration_apply(db: Session = Depends(get_db)):
    return safe_copy_migration_apply_assistant(db)


@router.get("/release-governance/rollback-drill-automation")
def api_rollback_drill_automation(db: Session = Depends(get_db)):
    return rollback_drill_automation_plan(db)
