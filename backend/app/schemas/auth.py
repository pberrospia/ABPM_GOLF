from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ReportBase(BaseModel):
    filename: str
    patient_name: Optional[str] = None
    exam_date: Optional[datetime] = None


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    owner_id: int
    storage_path: Path


class ReportUpdate(ReportBase):
    pass


class ABPMSummary(BaseModel):
    systolic_mean: float
    diastolic_mean: float


class ABPMMetrics(BaseModel):
    systolic_values: list[int]
    diastolic_values: list[int]
