from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.stable_milestone_service import v10_installer_checklist, v10_stable_milestone_report

router = APIRouter(prefix="/api", tags=["v10-stable-milestone"])


@router.get("/release-governance/v10-stable-milestone-report")
def api_v10_stable_milestone_report(db: Session = Depends(get_db)):
    return v10_stable_milestone_report(db)


@router.get("/release-governance/v10-installer-checklist")
def api_v10_installer_checklist():
    return v10_installer_checklist()
