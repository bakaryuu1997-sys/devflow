from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RequirementChangeCreate(BaseModel):
    requirement_key: str
    old_text: str = ""
    new_text: str


class RequirementChangeRead(BaseModel):
    id: int
    project_id: int
    requirement_key: str
    old_text: str
    new_text: str
    changed_fields: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TraceLinkCreate(BaseModel):
    requirement_key: str
    link_type: str
    target_key: str
    title: str = ""
    status: str = "Open"
    module: str = "general"


class TraceLinkRead(TraceLinkCreate):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TraceabilityRow(BaseModel):
    requirement_key: str
    requirement_title: str
    task_count: int
    api_count: int
    test_count: int
    bug_count: int
    commit_count: int
    risk: str
    warnings: list[str]


class ImpactAnalysisRead(BaseModel):
    requirement_key: str
    impacted_tasks: list[str]
    impacted_apis: list[str]
    impacted_tests: list[str]
    impacted_bugs: list[str]
    suggested_actions: list[str]


class CodeChangeAnalyzeRequest(BaseModel):
    source: str = "manual"
    files: list[str]


class CodeChangeRead(BaseModel):
    id: int
    project_id: int
    source: str
    file_path: str
    area: str
    severity: str
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnvGuardRequest(BaseModel):
    content: str
    required_keys: list[str] = []


class EnvFinding(BaseModel):
    key: str
    severity: str
    message: str
    blocking: bool


class BugPatternRow(BaseModel):
    module: str
    open_bugs: int
    critical_or_high: int
    reopened: int
    risk: str


class AdvancedReadinessRead(BaseModel):
    project_id: int
    score: int
    status: str
    blockers: list[str]
    warnings: list[str]
    recommendations: list[str]
