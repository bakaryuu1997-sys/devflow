from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.time_utils import utc_now


class SignedRehearsalArtifact(Base):
    __tablename__ = "signed_rehearsal_artifacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artifact_type: Mapped[str] = mapped_column(String(80), default="production-rehearsal")
    operator_name: Mapped[str] = mapped_column(String(160), default="")
    reviewer_name: Mapped[str] = mapped_column(String(160), default="")
    signature_text: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(60), default="Signed")
    notes: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class OperatorApprovalRecord(Base):
    __tablename__ = "operator_approval_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signed_artifact_id: Mapped[int] = mapped_column(ForeignKey("signed_rehearsal_artifacts.id"), index=True)
    approver_name: Mapped[str] = mapped_column(String(160), default="")
    approval_phrase: Mapped[str] = mapped_column(String(160), default="")
    status: Mapped[str] = mapped_column(String(60), default="Approved")
    approval_note: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
