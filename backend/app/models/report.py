from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    patient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    raw_metrics: Mapped[dict[str, Any]] = mapped_column(JSON)
    analysis: Mapped[dict[str, Any]] = mapped_column(JSON)
    source_pdf_path: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    conclusions: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    finalized_pdf_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update_timestamp(self) -> None:
        self.updated_at = datetime.utcnow()
