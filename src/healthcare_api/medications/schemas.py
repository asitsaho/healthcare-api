import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from healthcare_api.medications.models import MedicationStatus


class MedicationBase(BaseModel):
    patient_id: uuid.UUID
    medical_record_id: uuid.UUID
    medicine_name: str = Field(min_length=1, max_length=255)
    dosage: str | None = Field(default=None, max_length=100)
    frequency: str | None = Field(default=None, max_length=100)
    start_date: datetime.date
    end_date: datetime.date | None = None
    status: MedicationStatus = MedicationStatus.ACTIVE


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    patient_id: uuid.UUID | None = None
    medical_record_id: uuid.UUID | None = None
    medicine_name: str | None = Field(default=None, min_length=1, max_length=255)
    dosage: str | None = Field(default=None, max_length=100)
    frequency: str | None = Field(default=None, max_length=100)
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    status: MedicationStatus | None = None


class MedicationRead(MedicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_by: uuid.UUID
    updated_at: datetime.datetime


class MedicationList(BaseModel):
    items: list[MedicationRead]
    limit: int
    offset: int
    total: int
