from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.end_to_end_rehearsal_service import end_to_end_governance_rehearsal, list_governance_rehearsals, record_governance_rehearsal

router = APIRouter(prefix="/api", tags=["v9-9-end-to-end-rehearsal"])


@router.get("/release-governance/end-to-end-governance-rehearsal")
def api_end_to_end_governance_rehearsal(db: Session = Depends(get_db)):
    return end_to_end_governance_rehearsal(db)


@router.post("/release-governance/governance-rehearsal-records")
def api_record_governance_rehearsal(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return record_governance_rehearsal(db, payload)


@router.get("/release-governance/governance-rehearsal-records")
def api_list_governance_rehearsals(db: Session = Depends(get_db)):
    return list_governance_rehearsals(db)
