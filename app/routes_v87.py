from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_rehearsal_service import operator_signoff_checklist, production_upgrade_rehearsal_report

router = APIRouter(prefix="/api", tags=["v8-7-production-rehearsal"])


@router.get("/release-governance/production-upgrade-rehearsal-report")
def api_production_upgrade_rehearsal_report(db: Session = Depends(get_db)):
    return production_upgrade_rehearsal_report(db)


@router.get("/release-governance/operator-signoff-checklist")
def api_operator_signoff_checklist(db: Session = Depends(get_db)):
    return operator_signoff_checklist(db)
