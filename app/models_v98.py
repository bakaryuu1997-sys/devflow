from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.time_utils import utc_now


class FinalSignedEvidenceBundle(Base):
    __tablename__ = "final_signed_evidence_bundles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manifest_hash: Mapped[str] = mapped_column(String(128), index=True)
    bundle_hash: Mapped[str] = mapped_column(String(128), index=True)
    verifier_evidence_id: Mapped[int] = mapped_column(Integer, default=0)
    profile_name: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(80), default="Draft")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
