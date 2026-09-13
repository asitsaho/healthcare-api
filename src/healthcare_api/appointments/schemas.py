import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from healthcare_api.appointments.models import AppointmentStatus, AppointmentType


class AppointmentBase(BaseModel):
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_at: datetime.datetime
    appointment_type: AppointmentType
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    patient_id: uuid.UUID | None = None
    doctor_id: uuid.UUID | None = None
    appointment_at: datetime.datetime | None = None
    appointment_type: AppointmentType | None = None
    status: AppointmentStatus | None = None
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class AppointmentRead(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_by: uuid.UUID
    updated_at: datetime.datetime


class AppointmentList(BaseModel):
    items: list[AppointmentRead]
    limit: int
    offset: int
    total: int
