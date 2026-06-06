from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequirementCreate(BaseModel):
    key: str
    title: str
    priority: str = "Medium"
    status: str = "Open"


class RequirementUpdate(BaseModel):
    title: str | None = None
    priority: str | None = None
    status: str | None = None


class RequirementRead(RequirementCreate):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkItemCreate(BaseModel):
    requirement_id: int | None = None
    kind: str
    title: str
    status: str = "Open"
    severity: str = "Medium"


class WorkItemUpdate(BaseModel):
    requirement_id: int | None = None
    status: str | None = None
    severity: str | None = None
    title: str | None = None


class WorkItemPlaceholderCreate(BaseModel):
    kind: str


class WorkItemConvertPlaceholder(BaseModel):
    title: str
    status: str = "In Progress"
    severity: str = "Medium"


class WorkItemRead(WorkItemCreate):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskRead(BaseModel):
    id: int
    project_id: int
    requirement_id: int | None
    rule_id: str
    title: str
    message: str
    severity: str
    blocking: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReleaseCreate(BaseModel):
    version: str


class ReleaseRead(BaseModel):
    id: int
    project_id: int
    version: str
    status: str
    readiness_score: int
    gate_passed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)
    role: str = "admin"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ReleaseSignOffCreate(BaseModel):
    approved_by: str = "Release owner"
    approval_note: str = ""


class ReleaseRetrospectiveCreate(BaseModel):
    signoff_id: int | None = None
    author: str = "Release owner"
    what_went_well: str = ""
    what_to_improve: str = ""
    action_items: str = ""


class ReleaseLearningItemCreate(BaseModel):
    title: str
    prevention_action: str
    source: str = "manual"
    status: str = "Open"
    owner: str = ""
    due_date: str = ""


class ReleaseLearningItemStatusUpdate(BaseModel):
    status: str


class ReleaseLearningItemPlanningUpdate(BaseModel):
    owner: str | None = None
    due_date: str | None = None
    status: str | None = None
