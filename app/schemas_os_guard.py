from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InboxItemCreate(BaseModel):
    title: str
    source: str = "manual"
    priority: str = "Medium"


class InboxItemRead(InboxItemCreate):
    id: int
    project_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionCreate(BaseModel):
    title: str
    context: str = ""
    decision: str = ""


class DecisionRead(DecisionCreate):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityRead(BaseModel):
    id: int
    project_id: int | None
    action: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GuardFindingRead(BaseModel):
    id: int
    project_id: int
    guard_type: str
    filename: str
    severity: str
    title: str
    message: str
    blocking: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceRead(BaseModel):
    project_id: int
    release_id: int | None = None
    content: str
