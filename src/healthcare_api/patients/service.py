import datetime
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_api.appointments.models import Appointment
from healthcare_api.medical_records.models import MedicalRecord
from healthcare_api.patients.exceptions import (
    DuplicatePatientNumberError,
    InvalidDateOfBirthError,
    PatientHasDependentRecordsError,
    PatientNotFoundError,
)
from healthcare_api.patients.models import Gender, Patient
from healthcare_api.patients.schemas import PatientCreate, PatientUpdate


def _validate_date_of_birth(date_of_birth: datetime.date) -> None:
    if date_of_birth > datetime.date.today():  # noqa: DTZ011
        raise InvalidDateOfBirthError("date_of_birth cannot be in the future")


async def create_patient(db: AsyncSession, data: PatientCreate, actor_id: uuid.UUID) -> Patient:
    _validate_date_of_birth(data.date_of_birth)

    patient = Patient(
        **data.model_dump(),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(patient)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicatePatientNumberError(
            f"Patient number '{data.patient_number}' already exists"
        ) from exc
    await db.refresh(patient)
    return patient


async def get_patient(db: AsyncSession, patient_id: uuid.UUID) -> Patient:
    patient = await db.get(Patient, patient_id)
    if patient is None:
        raise PatientNotFoundError(f"Patient {patient_id} not found")
    return patient


async def list_patients(
    db: AsyncSession,
    *,
    name: str | None = None,
    patient_number: str | None = None,
    gender: Gender | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Patient], int]:
    stmt = select(Patient)

    if name:
        pattern = f"%{name.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Patient.first_name).like(pattern),
                func.lower(Patient.last_name).like(pattern),
            )
        )
    if patient_number:
        stmt = stmt.where(Patient.patient_number == patient_number)
    if gender:
        stmt = stmt.where(Patient.gender == gender)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Patient.created_at.desc()).limit(limit).offset(offset)
    patients = list((await db.scalars(stmt)).all())
    return patients, total


async def update_patient(
    db: AsyncSession, patient_id: uuid.UUID, data: PatientUpdate, actor_id: uuid.UUID
) -> Patient:
    patient = await get_patient(db, patient_id)

    updates = data.model_dump(exclude_unset=True)
    if "date_of_birth" in updates and updates["date_of_birth"] is not None:
        _validate_date_of_birth(updates["date_of_birth"])

    for field, value in updates.items():
        setattr(patient, field, value)
    patient.updated_by = actor_id

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicatePatientNumberError(
            f"Patient number '{updates.get('patient_number')}' already exists"
        ) from exc
    await db.refresh(patient)
    return patient


async def delete_patient(db: AsyncSession, patient_id: uuid.UUID) -> None:
    patient = await get_patient(db, patient_id)

    has_appointment = await db.scalar(
        select(Appointment.id).where(Appointment.patient_id == patient_id).limit(1)
    )
    has_medical_record = await db.scalar(
        select(MedicalRecord.id).where(MedicalRecord.patient_id == patient_id).limit(1)
    )
    if has_appointment is not None or has_medical_record is not None:
        raise PatientHasDependentRecordsError(
            f"Patient {patient_id} has dependent appointments or medical records "
            "and cannot be deleted"
        )

    await db.delete(patient)
    await db.commit()
