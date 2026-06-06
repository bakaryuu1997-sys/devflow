from datetime import datetime
from hashlib import sha256
from app.time_utils import utc_now
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, event, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class Requirement(Base):
    __tablename__ = "requirements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    key: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(255))
    priority: Mapped[str] = mapped_column(String(40), default="Medium")
    status: Mapped[str] = mapped_column(String(40), default="Open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class WorkItem(Base):
    __tablename__ = "work_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_id: Mapped[int | None] = mapped_column(ForeignKey("requirements.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40), default="Open")
    severity: Mapped[str] = mapped_column(String(40), default="Medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class RequirementReview(Base):
    __tablename__ = "requirement_reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), index=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class RiskEvent(Base):
    __tablename__ = "risk_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_id: Mapped[int | None] = mapped_column(ForeignKey("requirements.id"), nullable=True)
    rule_id: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(40))
    blocking: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class Release(Base):
    __tablename__ = "releases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    version: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="Draft")
    readiness_score: Mapped[int] = mapped_column(Integer, default=0)
    gate_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class ReleaseSignOff(Base):
    __tablename__ = "release_signoffs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    release_id: Mapped[int | None] = mapped_column(ForeignKey("releases.id"), nullable=True)
    release_version: Mapped[str] = mapped_column(String(80), default="unassigned")
    approved_by: Mapped[str] = mapped_column(String(160), default="Release owner")
    approval_note: Mapped[str] = mapped_column(Text, default="")
    snapshot: Mapped[str] = mapped_column(Text, default="")
    snapshot_json: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class ReleaseRetrospective(Base):
    __tablename__ = "release_retrospectives"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    signoff_id: Mapped[int | None] = mapped_column(ForeignKey("release_signoffs.id"), nullable=True)
    author: Mapped[str] = mapped_column(String(160), default="Release owner")
    what_went_well: Mapped[str] = mapped_column(Text, default="")
    what_to_improve: Mapped[str] = mapped_column(Text, default="")
    action_items: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class ReleaseLearningItem(Base):
    __tablename__ = "release_learning_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    source: Mapped[str] = mapped_column(String(120), default="manual")
    title: Mapped[str] = mapped_column(String(255))
    prevention_action: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="Open")
    owner: Mapped[str] = mapped_column(String(160), default="")
    due_date: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class ScopeDecisionAudit(Base):
    __tablename__ = "scope_decision_audits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    learning_item_id: Mapped[int] = mapped_column(ForeignKey("release_learning_items.id"), index=True)
    old_status: Mapped[str] = mapped_column(String(40), default="")
    new_status: Mapped[str] = mapped_column(String(40), default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class InboxItem(Base):
    __tablename__ = "inbox_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(80), default="manual")
    priority: Mapped[str] = mapped_column(String(40), default="Medium")
    status: Mapped[str] = mapped_column(String(40), default="Open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class Decision(Base):
    __tablename__ = "decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    context: Mapped[str] = mapped_column(Text, default="")
    decision: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    previous_hash: Mapped[str] = mapped_column(String(64), default="")
    current_hash: Mapped[str] = mapped_column(String(64), default="")

@event.listens_for(ActivityLog, "before_insert")
def receive_before_insert(mapper, connection, target):
    try:
        result = connection.execute(text("SELECT current_hash FROM activity_logs ORDER BY id DESC LIMIT 1")).fetchone()
        prev_hash = result[0] if result and result[0] else "0" * 64
    except Exception:
        prev_hash = "0" * 64
    
    target.previous_hash = prev_hash
    
    if target.created_at is None:
        target.created_at = utc_now()
        
    if target.created_at.tzinfo is not None:
        from datetime import UTC
        target.created_at = target.created_at.astimezone(UTC).replace(tzinfo=None)
        
    created_str = str(target.created_at)
    project_id_str = str(target.project_id) if target.project_id else "None"
    
    payload = f"{target.action}:{target.message}:{created_str}:{project_id_str}:{prev_hash}"
    target.current_hash = sha256(payload.encode("utf-8")).hexdigest()
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class GuardFinding(Base):
    __tablename__ = "guard_findings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    guard_type: Mapped[str] = mapped_column(String(80), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    blocking: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class RequirementChange(Base):
    __tablename__ = "requirement_changes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_key: Mapped[str] = mapped_column(String(80), index=True)
    old_text: Mapped[str] = mapped_column(Text, default="")
    new_text: Mapped[str] = mapped_column(Text)
    changed_fields: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="Needs Review")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class TraceLink(Base):
    __tablename__ = "trace_links"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_key: Mapped[str] = mapped_column(String(80), index=True)
    link_type: Mapped[str] = mapped_column(String(40))
    target_key: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(40), default="Open")
    module: Mapped[str] = mapped_column(String(80), default="general")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class CodeChange(Base):
    __tablename__ = "code_changes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    source: Mapped[str] = mapped_column(String(80), default="manual")
    file_path: Mapped[str] = mapped_column(String(255))
    area: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class GitItem(Base):
    __tablename__ = "git_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    item_type: Mapped[str] = mapped_column(String(40), default="commit")
    ref: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(80), default="")
    changed_files: Mapped[str] = mapped_column(Text, default="")
    linked_key: Mapped[str] = mapped_column(String(80), default="")
    risk: Mapped[str] = mapped_column(String(40), default="Low")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
class RequirementDiff(Base):
    __tablename__ = "requirement_diffs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_key: Mapped[str] = mapped_column(String(80), index=True)
    change_type: Mapped[str] = mapped_column(String(40))
    old_title: Mapped[str] = mapped_column(String(255), default="")
    new_title: Mapped[str] = mapped_column(String(255), default="")
    old_priority: Mapped[str] = mapped_column(String(40), default="")
    new_priority: Mapped[str] = mapped_column(String(40), default="")
    risk: Mapped[str] = mapped_column(String(40), default="Low")
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
