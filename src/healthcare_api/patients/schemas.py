import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from healthcare_api.patients.models import Gender


class PatientBase(BaseModel):
    patient_number: str = Field(min_length=1, max_length=32)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: datetime.date
    gender: Gender
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=500)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    """All fields optional: PATCH only changes what the client supplies."""

    patient_number: str | None = Field(default=None, min_length=1, max_length=32)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: datetime.date | None = None
    gender: Gender | None = None
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=500)


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_by: uuid.UUID
    updated_at: datetime.datetime


class PatientList(BaseModel):
    items: list[PatientRead]
    limit: int
    offset: int
    total: int
