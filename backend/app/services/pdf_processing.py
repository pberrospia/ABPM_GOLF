from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

from app.services.abpm_analysis import ABPMMetrics
from app.utils.files import ensure_directory


class PDFProcessor:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        ensure_directory(self.storage_dir)

    def save_upload(self, data: bytes, filename: str) -> Path:
        target = self.storage_dir / filename
        target.write_bytes(data)
        return target

    def extract_text(self, pdf_path: Path) -> str:
        # Placeholder implementation. Replace with actual PDF parsing.
        return pdf_path.read_text(encoding="utf-8", errors="ignore") if pdf_path.exists() else ""

    def parse_metrics(self, extracted_text: str) -> ABPMMetrics:
        # Dummy parser: return canned values when no metrics detected.
        return ABPMMetrics(systolic_values=[120, 118, 122], diastolic_values=[80, 78, 82])


def locate_patient_metadata(extracted_text: str) -> Tuple[str | None, str | None]:
    # Placeholder metadata extractor.
    return "Paciente sin identificar", datetime.utcnow().strftime("%Y-%m-%d")
