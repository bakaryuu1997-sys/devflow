from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_operator_handoff_service import operator_handoff_package, production_upgrade_runbook

router = APIRouter(prefix="/api", tags=["v8-6-operator-handoff"])


@router.get("/release-governance/production-upgrade-runbook")
def api_production_upgrade_runbook(db: Session = Depends(get_db)):
    return production_upgrade_runbook(db)


@router.get("/release-governance/operator-handoff-package")
def api_operator_handoff_package(db: Session = Depends(get_db)):
    return operator_handoff_package(db)
