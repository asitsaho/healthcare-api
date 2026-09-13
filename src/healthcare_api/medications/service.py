import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_api.medical_records.models import MedicalRecord
from healthcare_api.medications.exceptions import (
    MedicationNotFoundError,
    MedicationPatientNotFoundError,
    MedicationRecordNotFoundError,
    MedicationRecordPatientMismatchError,
)
from healthcare_api.medications.models import Medication, MedicationStatus
from healthcare_api.medications.schemas import MedicationCreate, MedicationUpdate
from healthcare_api.patients.models import Patient


async def _ensure_patient_exists(db: AsyncSession, patient_id: uuid.UUID) -> None:
    if await db.get(Patient, patient_id) is None:
        raise MedicationPatientNotFoundError(f"Patient {patient_id} does not exist")


async def _get_medical_record_or_raise(
    db: AsyncSession, medical_record_id: uuid.UUID
) -> MedicalRecord:
    record = await db.get(MedicalRecord, medical_record_id)
    if record is None:
        raise MedicationRecordNotFoundError(f"Medical record {medical_record_id} does not exist")
    return record


def _ensure_record_belongs_to_patient(record: MedicalRecord, patient_id: uuid.UUID) -> None:
    if record.patient_id != patient_id:
        raise MedicationRecordPatientMismatchError(
            f"Medical record {record.id} does not belong to patient {patient_id}"
        )


async def create_medication(
    db: AsyncSession, data: MedicationCreate, actor_id: uuid.UUID
) -> Medication:
    await _ensure_patient_exists(db, data.patient_id)
    record = await _get_medical_record_or_raise(db, data.medical_record_id)
    _ensure_record_belongs_to_patient(record, data.patient_id)

    medication = Medication(**data.model_dump(), created_by=actor_id, updated_by=actor_id)
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def get_medication(db: AsyncSession, medication_id: uuid.UUID) -> Medication:
    medication = await db.get(Medication, medication_id)
    if medication is None:
        raise MedicationNotFoundError(f"Medication {medication_id} not found")
    return medication


async def list_medications(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID | None = None,
    medical_record_id: uuid.UUID | None = None,
    status: MedicationStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Medication], int]:
    stmt = select(Medication)

    if patient_id:
        stmt = stmt.where(Medication.patient_id == patient_id)
    if medical_record_id:
        stmt = stmt.where(Medication.medical_record_id == medical_record_id)
    if status:
        stmt = stmt.where(Medication.status == status)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Medication.start_date.desc()).limit(limit).offset(offset)
    medications = list((await db.scalars(stmt)).all())
    return medications, total


async def update_medication(
    db: AsyncSession, medication_id: uuid.UUID, data: MedicationUpdate, actor_id: uuid.UUID
) -> Medication:
    medication = await get_medication(db, medication_id)
    updates = data.model_dump(exclude_unset=True)

    new_patient_id = updates.get("patient_id", medication.patient_id)
    if "patient_id" in updates:
        await _ensure_patient_exists(db, new_patient_id)

    if "medical_record_id" in updates:
        record = await _get_medical_record_or_raise(db, updates["medical_record_id"])
        _ensure_record_belongs_to_patient(record, new_patient_id)

    for field, value in updates.items():
        setattr(medication, field, value)
    medication.updated_by = actor_id

    await db.commit()
    await db.refresh(medication)
    return medication


async def delete_medication(db: AsyncSession, medication_id: uuid.UUID) -> None:
    # Deleting a medication only ever removes that medication.
    medication = await get_medication(db, medication_id)
    await db.delete(medication)
    await db.commit()
