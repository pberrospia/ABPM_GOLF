from __future__ import annotations

from pathlib import Path

from app.models.report import Report, create_demo_report
from app.models.user import User
from app.schemas.auth import ABPMMetrics, ABPMSummary, ReportCreate


class ReportComposer:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def create_report(self, *, owner: User, payload: ReportCreate, pdf_bytes: bytes) -> Report:
        # Persist PDF to disk (placeholder behaviour)
        filename = payload.filename
        path = self.storage_dir / filename
        path.write_bytes(pdf_bytes)
        return create_demo_report(
            owner=owner,
            filename=filename,
            patient_name=payload.patient_name,
            exam_date=payload.exam_date,
            storage_dir=self.storage_dir,
        )

    async def summarize(self, metrics: ABPMMetrics) -> ABPMSummary:
        systolic_mean = sum(metrics.systolic_values) / max(len(metrics.systolic_values), 1)
        diastolic_mean = sum(metrics.diastolic_values) / max(len(metrics.diastolic_values), 1)
        return ABPMSummary(systolic_mean=systolic_mean, diastolic_mean=diastolic_mean)
