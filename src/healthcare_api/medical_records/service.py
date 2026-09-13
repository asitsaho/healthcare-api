import datetime
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_api.doctors.models import Doctor
from healthcare_api.medical_records.exceptions import (
    MedicalRecordDoctorNotFoundError,
    MedicalRecordNotFoundError,
    MedicalRecordPatientNotFoundError,
)
from healthcare_api.medical_records.models import MedicalRecord, RecordType
from healthcare_api.medical_records.schemas import MedicalRecordCreate, MedicalRecordUpdate
from healthcare_api.patients.models import Patient


async def _ensure_patient_exists(db: AsyncSession, patient_id: uuid.UUID) -> None:
    if await db.get(Patient, patient_id) is None:
        raise MedicalRecordPatientNotFoundError(f"Patient {patient_id} does not exist")


async def _ensure_doctor_exists(db: AsyncSession, doctor_id: uuid.UUID) -> None:
    if await db.get(Doctor, doctor_id) is None:
        raise MedicalRecordDoctorNotFoundError(f"Doctor {doctor_id} does not exist")


async def create_medical_record(
    db: AsyncSession, data: MedicalRecordCreate, actor_id: uuid.UUID
) -> MedicalRecord:
    await _ensure_patient_exists(db, data.patient_id)
    await _ensure_doctor_exists(db, data.doctor_id)

    record = MedicalRecord(**data.model_dump(), created_by=actor_id, updated_by=actor_id)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_medical_record(db: AsyncSession, record_id: uuid.UUID) -> MedicalRecord:
    record = await db.get(MedicalRecord, record_id)
    if record is None:
        raise MedicalRecordNotFoundError(f"Medical record {record_id} not found")
    return record


async def list_medical_records(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID | None = None,
    doctor_id: uuid.UUID | None = None,
    record_type: RecordType | None = None,
    from_date: datetime.date | None = None,
    to_date: datetime.date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[MedicalRecord], int]:
    stmt = select(MedicalRecord)

    if patient_id:
        stmt = stmt.where(MedicalRecord.patient_id == patient_id)
    if doctor_id:
        stmt = stmt.where(MedicalRecord.doctor_id == doctor_id)
    if record_type:
        stmt = stmt.where(MedicalRecord.record_type == record_type)
    if from_date:
        stmt = stmt.where(MedicalRecord.record_date >= from_date)
    if to_date:
        stmt = stmt.where(MedicalRecord.record_date <= to_date)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(MedicalRecord.record_date.desc()).limit(limit).offset(offset)
    records = list((await db.scalars(stmt)).all())
    return records, total


async def update_medical_record(
    db: AsyncSession, record_id: uuid.UUID, data: MedicalRecordUpdate, actor_id: uuid.UUID
) -> MedicalRecord:
    record = await get_medical_record(db, record_id)
    updates = data.model_dump(exclude_unset=True)

    if "patient_id" in updates:
        await _ensure_patient_exists(db, updates["patient_id"])
    if "doctor_id" in updates:
        await _ensure_doctor_exists(db, updates["doctor_id"])

    for field, value in updates.items():
        setattr(record, field, value)
    record.updated_by = actor_id

    await db.commit()
    await db.refresh(record)
    return record


async def delete_medical_record(db: AsyncSession, record_id: uuid.UUID) -> None:
    # Medications prescribed by this record have no independent lifecycle and
    # are removed with it by the database's `ON DELETE CASCADE`.
    record = await get_medical_record(db, record_id)
    await db.delete(record)
    await db.commit()
