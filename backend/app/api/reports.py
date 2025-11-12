from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
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
    session: SessionDep,
    current_user: CurrentUserDep,
    pdf: UploadFile = File(...),
    patient_name: str | None = Form(None),
    exam_date: str | None = Form(None),
) -> ReportRead:
    """Persist an uploaded ABPM report.

    The key detail is that ``session`` and ``current_user`` now rely on
    ``typing.Annotated`` dependency aliases without extra defaults, which keeps
    FastAPI's dependency analysis compatible with Pydantic v2.
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
