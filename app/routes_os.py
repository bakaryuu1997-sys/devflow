from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.models import ActivityLog, Decision, InboxItem, User
from app.os_service import today_focus
from app.schemas import ActivityRead, DecisionCreate, DecisionRead, InboxItemCreate, InboxItemRead

router = APIRouter(prefix="/api", tags=["os"])


@router.get("/projects/{project_id}/today")
def api_today(project_id: int, db: Session = Depends(get_db)):
    return today_focus(db, project_id)


@router.post("/projects/{project_id}/inbox", response_model=InboxItemRead)
def api_create_inbox(project_id: int, payload: InboxItemCreate, db: Session = Depends(get_db), _user: User = Depends(require_write)):
    item = InboxItem(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/projects/{project_id}/inbox", response_model=list[InboxItemRead])
def api_inbox(project_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(InboxItem).where(InboxItem.project_id == project_id)).all())


@router.patch("/inbox/{item_id}/close", response_model=InboxItemRead)
def api_close_inbox(item_id: int, db: Session = Depends(get_db), _user: User = Depends(require_write)):
    item = db.get(InboxItem, item_id)
    item.status = "Closed"
    db.commit()
    db.refresh(item)
    return item


@router.post("/projects/{project_id}/decisions", response_model=DecisionRead)
def api_create_decision(project_id: int, payload: DecisionCreate, db: Session = Depends(get_db), _user: User = Depends(require_write)):
    decision = Decision(project_id=project_id, **payload.model_dump())
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


@router.get("/projects/{project_id}/decisions", response_model=list[DecisionRead])
def api_decisions(project_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Decision).where(Decision.project_id == project_id)).all())


@router.get("/projects/{project_id}/activity", response_model=list[ActivityRead])
def api_activity(project_id: int, db: Session = Depends(get_db)):
    stmt = select(ActivityLog).where(ActivityLog.project_id == project_id).order_by(ActivityLog.id.desc())
    return list(db.scalars(stmt).all())
