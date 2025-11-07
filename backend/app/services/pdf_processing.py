from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional, Tuple

import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader

from app.services.abpm_analysis import ABPMMetrics

METRIC_PATTERNS = {
    "systolic_24h": re.compile(r"(?i)(?:promedio|media).{0,20}24h\D*(\d{2,3})"),
    "diastolic_24h": re.compile(r"(?i)(?:promedio|media).{0,20}24h.*?/(\d{2,3})"),
    "systolic_day": re.compile(r"(?i)(?:promedio|media).{0,20}(?:diurno|vigilia)\D*(\d{2,3})"),
    "diastolic_day": re.compile(r"(?i)(?:promedio|media).{0,20}(?:diurno|vigilia).*?/(\d{2,3})"),
    "systolic_night": re.compile(r"(?i)(?:promedio|media).{0,20}(?:nocturno|sueño|nocturna)\D*(\d{2,3})"),
    "diastolic_night": re.compile(r"(?i)(?:promedio|media).{0,20}(?:nocturno|sueño|nocturna).*?/(\d{2,3})"),
    "measurements_total": re.compile(r"(?i)(?:lecturas|mediciones).{0,10}total\D*(\d{1,3})"),
    "measurements_day": re.compile(r"(?i)(?:lecturas|mediciones).{0,10}(?:diurnas|vigilia)\D*(\d{1,3})"),
    "measurements_night": re.compile(r"(?i)(?:lecturas|mediciones).{0,10}(?:nocturnas|sueño)\D*(\d{1,3})"),
}


class PDFProcessor:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir

    def save_upload(self, file_bytes: bytes, filename: str) -> Path:
        target_path = self.storage_dir / filename
        target_path.write_bytes(file_bytes)
        return target_path

    def extract_text(self, pdf_path: Path) -> str:
        text_chunks = list(self._extract_text_natively(pdf_path))
        if text_chunks:
            return "\n".join(text_chunks)
        return self._extract_text_via_ocr(pdf_path)

    def _extract_text_natively(self, pdf_path: Path) -> Iterable[str]:
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    cleaned = text.strip()
                    if cleaned:
                        yield cleaned
        except Exception:  # pragma: no cover - defensive, we fallback to OCR
            return []

    def _extract_text_via_ocr(self, pdf_path: Path) -> str:
        images = convert_from_path(str(pdf_path))
        text_segments = []
        for image in images:
            text_segments.append(pytesseract.image_to_string(image, lang="spa+eng"))
        return "\n".join(text_segments)

    def parse_metrics(self, text: str) -> ABPMMetrics:
        kwargs = {}
        for key, pattern in METRIC_PATTERNS.items():
            match = pattern.search(text)
            if match:
                kwargs[key] = float(match.group(1)) if "measurements" not in key else int(match.group(1))
            else:
                kwargs[key] = None
        return ABPMMetrics(**kwargs)

    def load_pdf_reader(self, pdf_path: Path) -> PdfReader:
        with open(pdf_path, "rb") as handle:
            reader = PdfReader(handle)
            return reader


def locate_patient_metadata(text: str) -> Tuple[Optional[str], Optional[str]]:
    name_match = re.search(r"(?i)(?:paciente|patient)\s*[:\-]\s*([\w\sáéíóúÁÉÍÓÚ]+)", text)
    date_match = re.search(r"(?i)(?:fecha|date)\s*[:\-]\s*(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})", text)
    return (
        name_match.group(1).strip() if name_match else None,
        date_match.group(1).strip() if date_match else None,
    )
