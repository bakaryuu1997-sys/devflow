from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.time_utils import utc_now


class ExternalVerifierProfile(Base):
    __tablename__ = "external_verifier_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    adapter: Mapped[str] = mapped_column(String(80), default="ed25519-public-key")
    policy_preset: Mapped[str] = mapped_column(String(80), default="standard-release")
    key_reference: Mapped[str] = mapped_column(String(180), default="")
    status: Mapped[str] = mapped_column(String(60), default="Active")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
