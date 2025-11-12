from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_session
from app.models.user import User
from app.schemas.auth import ABPMMetrics, ReportCreate, ReportRead
from app.services.abpm_analysis import locate_patient_metadata
from app.services.pdf_processing import PDFProcessor
from app.services.report_generation import ReportComposer
from app.utils.files import sanitize_upload_filename

router = APIRouter(prefix="/reports", tags=["reports"])


def _get_pdf_processor() -> PDFProcessor:
    return PDFProcessor(settings.storage_dir)


def _get_report_composer() -> ReportComposer:
    return ReportComposer(settings.storage_dir)


@router.post("/upload", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def upload_report(
    pdf: UploadFile = File(...),
    patient_name: Annotated[str | None, Form(None)] = None,
    exam_date: Annotated[str | None, Form(None)] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ReportRead:
    """Persist an uploaded ABPM report.

    The key detail is that ``session`` and ``current_user`` now rely on the
    traditional ``Depends`` default pattern, which is compatible with Pydantic v2
    and avoids the FastAPI assertion raised previously.
    """

    _ = session  # Session would be used for persistence in a full implementation.
    filename = sanitize_upload_filename(pdf.filename or "abpm_report.pdf")
    pdf_bytes = await pdf.read()

    if not pdf_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El PDF está vacío")

    composer = _get_report_composer()
    processor = _get_pdf_processor()

    await processor.save_upload(filename, pdf_bytes)

    exam_dt = datetime.fromisoformat(exam_date) if exam_date else None
    payload = ReportCreate(filename=filename, patient_name=patient_name, exam_date=exam_dt)
    report = await composer.create_report(owner=current_user, payload=payload, pdf_bytes=pdf_bytes)

    patient_name_meta, exam_date_meta = locate_patient_metadata(report.storage_path)
    metrics = ABPMMetrics(systolic_values=[120, 122, 118], diastolic_values=[80, 78, 82])
    return ReportRead(
        id=report.id,
        owner_id=report.owner_id,
        filename=report.filename,
        patient_name=patient_name_meta or report.patient_name,
        exam_date=exam_date_meta or report.exam_date,
        storage_path=report.storage_path,
    )
