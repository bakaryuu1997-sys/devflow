from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.time_utils import utc_now


class PublicVerifierEvidenceAttachment(Base):
    __tablename__ = "public_verifier_evidence_attachments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adapter: Mapped[str] = mapped_column(String(80), default="ed25519-public-key")
    payload_hash: Mapped[str] = mapped_column(String(128), index=True)
    signature_hash: Mapped[str] = mapped_column(String(128), default="")
    public_key_hash: Mapped[str] = mapped_column(String(128), default="")
    signer_name: Mapped[str] = mapped_column(String(160), default="")
    key_reference: Mapped[str] = mapped_column(String(180), default="")
    evidence_reference: Mapped[str] = mapped_column(String(180), default="")
    verification_status: Mapped[str] = mapped_column(String(80), default="Needs Review")
    gate_status: Mapped[str] = mapped_column(String(80), default="Not Gate-Ready")
    findings: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
