from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_release
from app.release_prevention_execution_service import (
    escalate_learning_item,
    overdue_risk_escalations,
    prevention_execution_board,
)

router = APIRouter(prefix="/api", tags=["v7-5-prevention-execution"])


class PreventionEscalationRequest(BaseModel):
    reason: str = ""


@router.get("/projects/{project_id}/prevention-execution-board")
def api_prevention_execution_board(project_id: int, db: Session = Depends(get_db)):
    return prevention_execution_board(db, project_id)


@router.get("/projects/{project_id}/overdue-risk-escalations")
def api_overdue_risk_escalations(project_id: int, db: Session = Depends(get_db)):
    return overdue_risk_escalations(db, project_id)


@router.post("/release-learning-items/{item_id}/escalate")
def api_escalate_learning_item(
    item_id: int,
    payload: PreventionEscalationRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_release),
):
    result = escalate_learning_item(db, item_id, payload.reason)
    if not result:
        raise HTTPException(404, "Release learning item not found")
    return result
