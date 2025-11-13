from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from app.schemas.auth import ABPMSummary


@dataclass
class ABPMMetrics:
    systolic_values: Sequence[float]
    diastolic_values: Sequence[float]

    def as_dict(self) -> dict[str, list[float]]:
        return {
            "systolic_values": list(self.systolic_values),
            "diastolic_values": list(self.diastolic_values),
        }


def summarize_metrics(metrics: ABPMMetrics) -> ABPMSummary:
    systolic_mean = mean(metrics.systolic_values) if metrics.systolic_values else 0.0
    diastolic_mean = mean(metrics.diastolic_values) if metrics.diastolic_values else 0.0
    return ABPMSummary(systolic_mean=systolic_mean, diastolic_mean=diastolic_mean)
