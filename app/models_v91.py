from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.time_utils import utc_now


class SignedPayloadVerificationRecord(Base):
    __tablename__ = "signed_payload_verification_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(128), index=True)
    manifest_hash: Mapped[str] = mapped_column(String(128), default="")
    bundle_hash: Mapped[str] = mapped_column(String(128), default="")
    signature_algorithm: Mapped[str] = mapped_column(String(80), default="external")
    signer_name: Mapped[str] = mapped_column(String(160), default="")
    signature_reference: Mapped[str] = mapped_column(String(160), default="")
    signature_hash: Mapped[str] = mapped_column(String(128), default="")
    verification_status: Mapped[str] = mapped_column(String(80), default="Needs Review")
    notes: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class TimestampTokenEvidenceAttachment(Base):
    __tablename__ = "timestamp_token_evidence_attachments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    handoff_id: Mapped[int] = mapped_column(Integer, default=0)
    payload_hash: Mapped[str] = mapped_column(String(128), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), default="")
    timestamp_authority: Mapped[str] = mapped_column(String(160), default="")
    token_reference: Mapped[str] = mapped_column(String(160), default="")
    verification_status: Mapped[str] = mapped_column(String(80), default="Needs Review")
    notes: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
