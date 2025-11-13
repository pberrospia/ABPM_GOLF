from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ReportBase(BaseModel):
    patient_name: Optional[str] = None
    exam_date: Optional[date] = None
    conclusions: Optional[str] = None
    recommendations: Optional[str] = None


class ReportCreate(ReportBase):
    raw_text: str
    raw_metrics: dict[str, Any]
    analysis: dict[str, Any]
    source_pdf_path: str
    status: str = "draft"


class ReportUpdate(ReportBase):
    status: Optional[str] = None
    finalized_pdf_path: Optional[str] = None


class ReportRead(BaseModel):
    id: int
    owner_id: int
    patient_name: Optional[str]
    exam_date: Optional[date]
    raw_text: str
    raw_metrics: dict[str, Any]
    analysis: dict[str, Any]
    source_pdf_path: str
    status: str
    conclusions: Optional[str] = None
    recommendations: Optional[str] = None
    finalized_pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ABPMSummary(BaseModel):
    systolic_mean: float
    diastolic_mean: float


class ReportFinalized(BaseModel):
    report: ReportRead
    summary: ABPMSummary
    pdf_path: str
