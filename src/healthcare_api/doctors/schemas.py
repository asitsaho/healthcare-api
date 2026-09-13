import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DoctorBase(BaseModel):
    doctor_number: str = Field(min_length=1, max_length=32)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialization: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    doctor_number: str | None = Field(default=None, min_length=1, max_length=32)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    specialization: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None


class DoctorRead(DoctorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_by: uuid.UUID
    updated_at: datetime.datetime


class DoctorList(BaseModel):
    items: list[DoctorRead]
    limit: int
    offset: int
    total: int
