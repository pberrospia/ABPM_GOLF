from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import CurrentUser, DBSession
from app.models import Report
from app.schemas.auth import ABPMSummary, ReportCreate, ReportRead, ReportUpdate
from app.services.abpm_analysis import ABPMMetrics, summarize_metrics
from app.services.pdf_processing import PDFProcessor, locate_patient_metadata
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
    patient_name: str = Form(None),
    exam_date: str = Form(None),
    session: DBSession,
    current_user: CurrentUser,
) -> ReportRead:
    pdf_bytes = await pdf.read()
    sanitized_name = sanitize_upload_filename(pdf.filename, fallback="report.pdf")
    filename = (
        f"report_{current_user.id}_{int(datetime.utcnow().timestamp())}_{sanitized_name}"
    )
    processor = _get_pdf_processor()
    pdf_path = processor.save_upload(pdf_bytes, filename)

    extracted_text = processor.extract_text(pdf_path)
    metrics = processor.parse_metrics(extracted_text)
    summary = summarize_metrics(metrics)

    patient, date_str = locate_patient_metadata(extracted_text)
    patient_name = patient_name or patient or "Paciente sin identificar"
    parsed_exam_date = _parse_exam_date(exam_date or date_str) or datetime.utcnow().date()

    report = Report(
        owner_id=current_user.id,
        patient_name=patient_name,
        exam_date=parsed_exam_date,
        raw_text=extracted_text,
        raw_metrics=metrics.as_dict(),
        analysis=summary.model_dump(),
        source_pdf_path=str(pdf_path),
        status="draft",
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)

    return ReportRead.model_validate(report)


@router.get("/", response_model=List[ReportRead])
async def list_reports(session: DBSession, current_user: CurrentUser) -> List[ReportRead]:
    result = await session.execute(select(Report).where(Report.owner_id == current_user.id).order_by(Report.created_at.desc()))
    reports = result.scalars().all()
    return [ReportRead.model_validate(report) for report in reports]


@router.get("/{report_id}", response_model=ReportRead)
async def get_report(report_id: int, session: DBSession, current_user: CurrentUser) -> ReportRead:
    report = await _get_owned_report(report_id, session, current_user)
    return ReportRead.model_validate(report)


@router.put("/{report_id}", response_model=ReportRead)
async def update_report(
    report_id: int,
    payload: ReportUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> ReportRead:
    report = await _get_owned_report(report_id, session, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    report.updated_at = datetime.utcnow()
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return ReportRead.model_validate(report)


@router.post("/{report_id}/finalize", response_model=ReportRead)
async def finalize_report(
    report_id: int,
    conclusions: str = Form(""),
    recommendations: str = Form(""),
    session: DBSession,
    current_user: CurrentUser,
) -> ReportRead:
    report = await _get_owned_report(report_id, session, current_user)
    if not report.analysis:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El informe no tiene análisis disponible")

    summary = ABPMSummary.model_validate(report.analysis)

    composer = _get_report_composer()
    signature_path = None
    if current_user.signature_path:
        signature_path = settings.storage_dir / Path(current_user.signature_path).name
        if not signature_path.exists():
            signature_path = Path(current_user.signature_path)

    finalized_pdf = composer.build_summary_pdf(
        source_pdf=Path(report.source_pdf_path),
        summary=summary,
        conclusions=conclusions,
        recommendations=recommendations,
        patient_name=report.patient_name,
        exam_date=datetime.combine(report.exam_date, datetime.min.time()),
        clinician_name=current_user.full_name,
        signature_path=signature_path,
    )

    report.conclusions = conclusions
    report.recommendations = recommendations
    report.finalized_pdf_path = str(finalized_pdf)
    report.status = "finalizado"
    report.updated_at = datetime.utcnow()

    session.add(report)
    await session.commit()
    await session.refresh(report)
    return ReportRead.model_validate(report)


async def _get_owned_report(report_id: int, session: AsyncSession, current_user: CurrentUser) -> Report:
    result = await session.execute(select(Report).where(Report.id == report_id, Report.owner_id == current_user.id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Informe no encontrado")
    return report


def _parse_exam_date(value: str | None):
    if not value:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
