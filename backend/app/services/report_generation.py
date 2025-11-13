from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.schemas.auth import ABPMSummary


class ReportComposer:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def build_summary_pdf(
        self,
        *,
        source_pdf: Path,
        summary: ABPMSummary,
        conclusions: str,
        recommendations: str,
        patient_name: str,
        exam_date: datetime,
        clinician_name: str,
        signature_path: Path | None,
    ) -> Path:
        output_path = self.storage_dir / f"summary_{source_pdf.stem}.pdf"
        content = [
            f"Paciente: {patient_name}",
            f"Fecha del examen: {exam_date.strftime('%d/%m/%Y')}",
            f"Clínico: {clinician_name}",
            "",
            f"Promedio Sistólico: {summary.systolic_mean:.1f}",
            f"Promedio Diastólico: {summary.diastolic_mean:.1f}",
            "",
            "Conclusiones:",
            conclusions or "(Sin conclusiones)",
            "",
            "Recomendaciones:",
            recommendations or "(Sin recomendaciones)",
        ]

        if signature_path and signature_path.exists():
            content.append("")
            content.append(f"Firma digital adjunta: {signature_path}")

        output_path.write_text("\n".join(content), encoding="utf-8")
        return output_path
