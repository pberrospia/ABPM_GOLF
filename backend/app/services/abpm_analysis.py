from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.schemas.auth import ABPMMetrics, ABPMSummary


def locate_patient_metadata(_pdf_path: Path) -> tuple[str | None, datetime | None]:
    """Return placeholder metadata extracted from the PDF."""

    return "Paciente Demo", datetime.now()


def summarize_metrics(metrics: ABPMMetrics) -> ABPMSummary:
    systolic_mean = sum(metrics.systolic_values) / max(len(metrics.systolic_values), 1)
    diastolic_mean = sum(metrics.diastolic_values) / max(len(metrics.diastolic_values), 1)
    return ABPMSummary(systolic_mean=systolic_mean, diastolic_mean=diastolic_mean)
