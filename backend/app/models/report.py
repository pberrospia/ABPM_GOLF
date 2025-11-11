from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_name = Column(String, nullable=False)
    exam_date = Column(Date, nullable=False)
    raw_text = Column(Text, nullable=True)
    raw_metrics = Column(JSON, nullable=True)
    analysis = Column(JSON, nullable=True)
    conclusions = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    source_pdf_path = Column(String, nullable=False)
    finalized_pdf_path = Column(String, nullable=True)
    status = Column(String, default="draft", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="reports")
