from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.production_migration_gate_service import final_production_upgrade_checklist, human_approved_real_migration_gate

router = APIRouter(prefix="/api", tags=["v8-5-production-migration-gate"])


@router.get("/release-governance/human-approved-real-migration-gate")
def api_human_approved_real_migration_gate(db: Session = Depends(get_db)):
    return human_approved_real_migration_gate(db)


@router.get("/release-governance/final-production-upgrade-checklist")
def api_final_production_upgrade_checklist(db: Session = Depends(get_db)):
    return final_production_upgrade_checklist(db)
