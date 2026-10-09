"""Pydantic schemas for Health Copilot MongoDB collections."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = None
    source_document_id: Optional[str] = None
    source_page_number: Optional[int] = None
    confidence: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserRecord(BaseRecord):
    user_id: str
    patient_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None


class DocumentRecord(BaseRecord):
    user_id: str
    patient_id: Optional[str] = None
    document_id: str
    title: str
    document_type: Optional[str] = None
    date: Optional[datetime] = None
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    cloudinary_public_id: Optional[str] = None
    cloudinary_secure_url: Optional[str] = None
    storage_provider: Optional[str] = None
    status: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    file_format: Optional[str] = None
    resource_type: Optional[str] = None


class DocumentPageRecord(BaseRecord):
    document_id: str
    page_number: int
    content: Optional[str] = None
    source_document_id: Optional[str] = None
    confidence: Optional[float] = None


class PrescriptionRecord(BaseRecord):
    user_id: str
    medicine_name: str
    dosage: Optional[str] = None
    unit: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = None
    instructions: Optional[str] = None
    prescription_date: Optional[datetime] = None
    confidence: Optional[float] = None
    source_document_id: Optional[str] = None
    source_page_number: Optional[int] = None


class LabResultRecord(BaseRecord):
    user_id: str
    test_name: str
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Literal[
        "WITHIN_RANGE",
        "BELOW_RANGE",
        "ABOVE_RANGE",
        "UNABLE_TO_DETERMINE",
    ] = "UNABLE_TO_DETERMINE"
    test_date: Optional[datetime] = None


class DiagnosticReportRecord(BaseRecord):
    user_id: str
    examination_type: str
    findings: Optional[str] = None
    impression: Optional[str] = None
    report_date: Optional[datetime] = None
    doctor_name: Optional[str] = None
    confidence: Optional[float] = None
    source_document_id: Optional[str] = None
    source_page_number: Optional[int] = None


class DischargeSummaryRecord(BaseRecord):
    user_id: str
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    diagnoses_explicitly_mentioned: List[str] = Field(default_factory=list)
    procedures: List[str] = Field(default_factory=list)
    medicines: List[str] = Field(default_factory=list)
    follow_up_instructions: Optional[str] = None
    source_document_id: Optional[str] = None
    source_page_number: Optional[int] = None
    confidence: Optional[float] = None


class TimelineEventRecord(BaseRecord):
    event_id: str
    user_id: str
    event_type: str
    date: datetime
    title: str
    description: Optional[str] = None
    source_document_id: Optional[str] = None
    source_page_number: Optional[int] = None


class WellnessRecord(BaseRecord):
    user_id: str
    weight: Optional[float] = None
    blood_pressure: Optional[str] = None
    blood_glucose: Optional[str] = None
    date: datetime
    source: Optional[str] = None


class HealthSummaryRecord(BaseRecord):
    summary_id: str
    user_id: str
    summary_text: str
    language: Optional[str] = None
    source_documents: List[str] = Field(default_factory=list)
