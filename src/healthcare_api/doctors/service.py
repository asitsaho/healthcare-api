import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_api.appointments.models import Appointment
from healthcare_api.doctors.exceptions import (
    DoctorHasDependentRecordsError,
    DoctorNotFoundError,
    DuplicateDoctorNumberError,
)
from healthcare_api.doctors.models import Doctor
from healthcare_api.doctors.schemas import DoctorCreate, DoctorUpdate
from healthcare_api.medical_records.models import MedicalRecord


async def create_doctor(db: AsyncSession, data: DoctorCreate, actor_id: uuid.UUID) -> Doctor:
    doctor = Doctor(**data.model_dump(), created_by=actor_id, updated_by=actor_id)
    db.add(doctor)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateDoctorNumberError(
            f"Doctor number '{data.doctor_number}' already exists"
        ) from exc
    await db.refresh(doctor)
    return doctor


async def get_doctor(db: AsyncSession, doctor_id: uuid.UUID) -> Doctor:
    doctor = await db.get(Doctor, doctor_id)
    if doctor is None:
        raise DoctorNotFoundError(f"Doctor {doctor_id} not found")
    return doctor


async def list_doctors(
    db: AsyncSession,
    *,
    name: str | None = None,
    specialization: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Doctor], int]:
    stmt = select(Doctor)

    if name:
        pattern = f"%{name.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Doctor.first_name).like(pattern),
                func.lower(Doctor.last_name).like(pattern),
            )
        )
    if specialization:
        stmt = stmt.where(func.lower(Doctor.specialization) == specialization.lower())

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Doctor.created_at.desc()).limit(limit).offset(offset)
    doctors = list((await db.scalars(stmt)).all())
    return doctors, total


async def update_doctor(
    db: AsyncSession, doctor_id: uuid.UUID, data: DoctorUpdate, actor_id: uuid.UUID
) -> Doctor:
    doctor = await get_doctor(db, doctor_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)
    doctor.updated_by = actor_id

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateDoctorNumberError("Doctor number already exists") from exc
    await db.refresh(doctor)
    return doctor


async def delete_doctor(db: AsyncSession, doctor_id: uuid.UUID) -> None:
    doctor = await get_doctor(db, doctor_id)

    has_appointment = await db.scalar(
        select(Appointment.id).where(Appointment.doctor_id == doctor_id).limit(1)
    )
    has_medical_record = await db.scalar(
        select(MedicalRecord.id).where(MedicalRecord.doctor_id == doctor_id).limit(1)
    )
    if has_appointment is not None or has_medical_record is not None:
        raise DoctorHasDependentRecordsError(
            f"Doctor {doctor_id} has dependent appointments or medical records "
            "and cannot be deleted"
        )

    await db.delete(doctor)
    await db.commit()
