from dataclasses import dataclass
from typing import Dict, Optional

from app.schemas.auth import ABPMSummary


@dataclass
class ABPMMetrics:
    systolic_24h: Optional[float] = None
    diastolic_24h: Optional[float] = None
    systolic_day: Optional[float] = None
    diastolic_day: Optional[float] = None
    systolic_night: Optional[float] = None
    diastolic_night: Optional[float] = None
    measurements_total: Optional[int] = None
    measurements_day: Optional[int] = None
    measurements_night: Optional[int] = None

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "systolic_24h": self.systolic_24h,
            "diastolic_24h": self.diastolic_24h,
            "systolic_day": self.systolic_day,
            "diastolic_day": self.diastolic_day,
            "systolic_night": self.systolic_night,
            "diastolic_night": self.diastolic_night,
            "measurements_total": self.measurements_total,
            "measurements_day": self.measurements_day,
            "measurements_night": self.measurements_night,
        }


EU_CLINICAL_THRESHOLDS = {
    "24h": (130, 80),
    "day": (135, 85),
    "night": (120, 70),
}


DIPPING_THRESHOLDS = {
    "riser": (-100.0, 0.0),
    "non-dipper": (0.0, 10.0),
    "dipper": (10.0, 20.0),
    "extreme dipper": (20.0, 100.0),
}


MEASUREMENT_MINIMUMS = {
    "total": 70,
    "day": 20,
    "night": 7,
}


class ABPMAnalyzer:
    def __init__(self, metrics: ABPMMetrics):
        self.metrics = metrics

    def classify(self) -> ABPMSummary:
        adequacy = self._evaluate_adequacy()
        pulse_pressure = self._compute_pulse_pressure()
        dipping = self._evaluate_dipping()
        classification, interpretation = self._evaluate_classification()

        return ABPMSummary(
            systolic_24h=self.metrics.systolic_24h,
            diastolic_24h=self.metrics.diastolic_24h,
            systolic_day=self.metrics.systolic_day,
            diastolic_day=self.metrics.diastolic_day,
            systolic_night=self.metrics.systolic_night,
            diastolic_night=self.metrics.diastolic_night,
            measurements_total=self.metrics.measurements_total,
            measurements_day=self.metrics.measurements_day,
            measurements_night=self.metrics.measurements_night,
            pulse_pressure_24h=pulse_pressure,
            dipping_pattern=dipping,
            classification=classification,
            interpretation=interpretation,
            adequacy=adequacy,
        )

    def _evaluate_adequacy(self) -> str:
        missing_counts = []
        for key, minimum in MEASUREMENT_MINIMUMS.items():
            value = getattr(self.metrics, f"measurements_{key}")
            if value is None:
                missing_counts.append(f"{key}: Dato insuficiente")
            elif value < minimum:
                missing_counts.append(f"{key}: insuficiente ({value}/{minimum})")
        if missing_counts:
            return "; ".join(missing_counts)
        return "Adecuado"

    def _compute_pulse_pressure(self) -> Optional[float]:
        if self.metrics.systolic_24h is None or self.metrics.diastolic_24h is None:
            return None
        return round(self.metrics.systolic_24h - self.metrics.diastolic_24h, 2)

    def _evaluate_dipping(self) -> Optional[str]:
        if self.metrics.systolic_day is None or self.metrics.systolic_night is None:
            return "Dato insuficiente"
        if self.metrics.systolic_day == 0:
            return "Dato insuficiente"
        drop_percentage = ((self.metrics.systolic_day - self.metrics.systolic_night) / self.metrics.systolic_day) * 100
        for label, (lower, upper) in DIPPING_THRESHOLDS.items():
            if lower <= drop_percentage < upper:
                return label
        return "Dato insuficiente"

    def _evaluate_classification(self) -> tuple[Optional[str], Optional[str]]:
        if self.metrics.systolic_24h is None or self.metrics.diastolic_24h is None:
            return "Dato insuficiente", "No se dispone de datos suficientes para clasificar"

        sbp24, dbp24 = self.metrics.systolic_24h, self.metrics.diastolic_24h
        sbp_day, dbp_day = self.metrics.systolic_day, self.metrics.diastolic_day
        sbp_night, dbp_night = self.metrics.systolic_night, self.metrics.diastolic_night

        def exceeds(value: Optional[float], threshold: float) -> bool:
            return value is not None and value >= threshold

        categories = []
        if exceeds(sbp24, EU_CLINICAL_THRESHOLDS["24h"][0]) or exceeds(dbp24, EU_CLINICAL_THRESHOLDS["24h"][1]):
            categories.append("Hipertensión sostenida (promedio 24h)")
        if exceeds(sbp_day, EU_CLINICAL_THRESHOLDS["day"][0]) or exceeds(dbp_day, EU_CLINICAL_THRESHOLDS["day"][1]):
            categories.append("Hipertensión diurna")
        if exceeds(sbp_night, EU_CLINICAL_THRESHOLDS["night"][0]) or exceeds(dbp_night, EU_CLINICAL_THRESHOLDS["night"][1]):
            categories.append("Hipertensión nocturna")

        if not categories:
            categories.append("Normotensión según guías ESC/ESH 2023")
            interpretation = "El estudio es compatible con control óptimo de la presión arterial."
        else:
            interpretation = "; ".join(categories)

        return "; ".join(categories), interpretation


def summarize_metrics(metrics: ABPMMetrics) -> ABPMSummary:
    analyzer = ABPMAnalyzer(metrics)
    return analyzer.classify()
