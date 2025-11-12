from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.models.user import User


@dataclass
class Report:
    id: int
    owner_id: int
    filename: str
    patient_name: str | None
    exam_date: datetime | None
    storage_path: Path


def create_demo_report(*, owner: User, filename: str, patient_name: str | None, exam_date: datetime | None, storage_dir: Path) -> Report:
    storage_path = storage_dir / filename
    storage_path.touch(exist_ok=True)
    return Report(
        id=1,
        owner_id=owner.id,
        filename=filename,
        patient_name=patient_name,
        exam_date=exam_date,
        storage_path=storage_path,
    )
