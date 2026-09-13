import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from healthcare_api.medical_records.models import RecordType


class MedicalRecordBase(BaseModel):
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    record_type: RecordType
    diagnosis: str | None = Field(default=None, max_length=500)
    treatment: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=2000)
    record_date: datetime.date


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    patient_id: uuid.UUID | None = None
    doctor_id: uuid.UUID | None = None
    record_type: RecordType | None = None
    diagnosis: str | None = Field(default=None, max_length=500)
    treatment: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=2000)
    record_date: datetime.date | None = None


class MedicalRecordRead(MedicalRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_by: uuid.UUID
    updated_at: datetime.datetime


class MedicalRecordList(BaseModel):
    items: list[MedicalRecordRead]
    limit: int
    offset: int
    total: int
