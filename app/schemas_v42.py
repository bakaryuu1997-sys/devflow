from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GitImportRequest(BaseModel):
    content: str
    item_type: str = "commit"


class GitItemRead(BaseModel):
    id: int
    project_id: int
    item_type: str
    ref: str
    title: str
    author: str
    status: str
    changed_files: str
    linked_key: str
    risk: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequirementDiffRequest(BaseModel):
    old_csv: str
    new_csv: str


class RequirementDiffRead(BaseModel):
    id: int
    project_id: int
    requirement_key: str
    change_type: str
    old_title: str
    new_title: str
    old_priority: str
    new_priority: str
    risk: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpenApiDeepDiffRequest(BaseModel):
    before: str
    after: str


class OpenApiDeepFinding(BaseModel):
    path: str
    method: str
    severity: str
    message: str
    blocking: bool


class WorkloadRow(BaseModel):
    owner: str
    open_items: int
    high_or_critical: int
    risky_git_items: int
    risk: str
