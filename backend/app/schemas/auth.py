from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    signature_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SignatureUpload(BaseModel):
    filename: str


class ReportBase(BaseModel):
    patient_name: str
    exam_date: date


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    conclusions: Optional[str]
    recommendations: Optional[str]
    status: Optional[str]


class ABPMSummary(BaseModel):
    systolic_24h: Optional[float]
    diastolic_24h: Optional[float]
    systolic_day: Optional[float]
    diastolic_day: Optional[float]
    systolic_night: Optional[float]
    diastolic_night: Optional[float]
    measurements_total: Optional[int]
    measurements_day: Optional[int]
    measurements_night: Optional[int]
    pulse_pressure_24h: Optional[float]
    dipping_pattern: Optional[str]
    classification: Optional[str]
    interpretation: Optional[str]
    adequacy: str

    class Config:
        orm_mode = True


class ReportRead(ReportBase):
    id: int
    raw_text: Optional[str]
    raw_metrics: Optional[dict]
    analysis: Optional[ABPMSummary]
    conclusions: Optional[str]
    recommendations: Optional[str]
    status: str
    source_pdf_path: str
    finalized_pdf_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
