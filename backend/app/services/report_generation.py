from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.schemas.auth import ABPMSummary


class ReportComposer:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir

    def build_summary_pdf(
        self,
        source_pdf: Path,
        summary: ABPMSummary,
        conclusions: str,
        recommendations: str,
        patient_name: str,
        exam_date: datetime,
        clinician_name: str,
        signature_path: Optional[Path] = None,
    ) -> Path:
        summary_pdf_path = self.storage_dir / f"summary_{source_pdf.stem}.pdf"
        self._create_summary_page(
            summary_pdf_path,
            summary,
            conclusions,
            recommendations,
            patient_name,
            exam_date,
            clinician_name,
            signature_path,
        )
        return self._merge_pdfs(source_pdf, summary_pdf_path)

    def _create_summary_page(
        self,
        target_path: Path,
        summary: ABPMSummary,
        conclusions: str,
        recommendations: str,
        patient_name: str,
        exam_date: datetime,
        clinician_name: str,
        signature_path: Optional[Path],
    ) -> None:
        packet = canvas.Canvas(str(target_path), pagesize=A4)
        width, height = A4
        margin = 20 * mm

        packet.setFont("Helvetica-Bold", 16)
        packet.drawString(margin, height - margin, "Informe ABPM")

        packet.setFont("Helvetica", 11)
        packet.drawString(margin, height - margin - 20, f"Paciente: {patient_name}")
        packet.drawString(margin, height - margin - 35, f"Fecha del examen: {exam_date:%d/%m/%Y}")
        packet.drawString(margin, height - margin - 50, f"Responsable: {clinician_name}")

        y_position = height - margin - 80
        packet.setFont("Helvetica-Bold", 13)
        packet.drawString(margin, y_position, "Resumen de métricas")
        y_position -= 20
        packet.setFont("Helvetica", 10)

        metric_lines = [
            f"Promedio 24h: {self._format_pressure(summary.systolic_24h, summary.diastolic_24h)}",
            f"Promedio diurno: {self._format_pressure(summary.systolic_day, summary.diastolic_day)}",
            f"Promedio nocturno: {self._format_pressure(summary.systolic_night, summary.diastolic_night)}",
            f"Mediciones (total/diurno/nocturno): {self._format_counts(summary)}",
            f"Presión de pulso 24h: {summary.pulse_pressure_24h if summary.pulse_pressure_24h is not None else 'Dato insuficiente'}",
            f"Patrón dipping: {summary.dipping_pattern or 'Dato insuficiente'}",
            f"Clasificación: {summary.classification or 'Dato insuficiente'}",
            f"Adecuación: {summary.adequacy}",
        ]
        for line in metric_lines:
            packet.drawString(margin, y_position, line)
            y_position -= 15

        y_position -= 10
        packet.setFont("Helvetica-Bold", 13)
        packet.drawString(margin, y_position, "Conclusiones")
        y_position -= 15
        packet.setFont("Helvetica", 10)
        for line in conclusions.splitlines() or ["(Sin conclusiones)"]:
            packet.drawString(margin, y_position, line)
            y_position -= 12

        y_position -= 10
        packet.setFont("Helvetica-Bold", 13)
        packet.drawString(margin, y_position, "Recomendaciones")
        y_position -= 15
        packet.setFont("Helvetica", 10)
        for line in recommendations.splitlines() or ["(Sin recomendaciones)"]:
            packet.drawString(margin, y_position, line)
            y_position -= 12

        if signature_path and signature_path.exists():
            packet.drawImage(str(signature_path), width - margin - 40 * mm, margin + 10 * mm, width=40 * mm, preserveAspectRatio=True, mask='auto')
            packet.setFont("Helvetica", 9)
            packet.drawString(width - margin - 40 * mm, margin + 5 * mm, "Firma autorizada")

        packet.save()

    def _merge_pdfs(self, source_pdf: Path, summary_pdf: Path) -> Path:
        merged_path = self.storage_dir / f"{source_pdf.stem}_firmado_{datetime.utcnow():%Y%m%d}.pdf"
        writer = PdfWriter()

        with open(source_pdf, "rb") as source_handle:
            reader = PdfReader(source_handle)
            for page in reader.pages:
                writer.add_page(page)

        with open(summary_pdf, "rb") as summary_handle:
            summary_reader = PdfReader(summary_handle)
            for page in summary_reader.pages:
                writer.add_page(page)

        with open(merged_path, "wb") as merged_handle:
            writer.write(merged_handle)

        return merged_path

    @staticmethod
    def _format_pressure(systolic: Optional[float], diastolic: Optional[float]) -> str:
        if systolic is None or diastolic is None:
            return "Dato insuficiente"
        return f"{int(systolic)}/{int(diastolic)} mmHg"

    @staticmethod
    def _format_counts(summary: ABPMSummary) -> str:
        total = summary.measurements_total if summary.measurements_total is not None else "?"
        day = summary.measurements_day if summary.measurements_day is not None else "?"
        night = summary.measurements_night if summary.measurements_night is not None else "?"
        return f"{total}/{day}/{night}"
