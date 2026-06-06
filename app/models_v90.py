from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.time_utils import utc_now


class ExternalTimestampHandoffRecord(Base):
    __tablename__ = "external_timestamp_handoff_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(128), index=True)
    manifest_hash: Mapped[str] = mapped_column(String(128), default="")
    bundle_hash: Mapped[str] = mapped_column(String(128), default="")
    timestamp_authority: Mapped[str] = mapped_column(String(160), default="")
    request_reference: Mapped[str] = mapped_column(String(160), default="")
    response_token_hash: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(60), default="Prepared")
    notes: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
