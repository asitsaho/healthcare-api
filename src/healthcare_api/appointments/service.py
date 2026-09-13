import datetime
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_api.appointments.exceptions import (
    AppointmentDoctorNotFoundError,
    AppointmentNotFoundError,
    AppointmentPatientNotFoundError,
    DoctorAlreadyBookedError,
)
from healthcare_api.appointments.models import Appointment, AppointmentStatus, AppointmentType
from healthcare_api.appointments.schemas import AppointmentCreate, AppointmentUpdate
from healthcare_api.doctors.models import Doctor
from healthcare_api.patients.models import Patient

# Statuses that still occupy the doctor's calendar slot.
_ACTIVE_STATUSES = (AppointmentStatus.SCHEDULED,)


async def _ensure_patient_exists(db: AsyncSession, patient_id: uuid.UUID) -> None:
    if await db.get(Patient, patient_id) is None:
        raise AppointmentPatientNotFoundError(f"Patient {patient_id} does not exist")


async def _ensure_doctor_exists(db: AsyncSession, doctor_id: uuid.UUID) -> None:
    if await db.get(Doctor, doctor_id) is None:
        raise AppointmentDoctorNotFoundError(f"Doctor {doctor_id} does not exist")


async def _ensure_doctor_not_double_booked(
    db: AsyncSession,
    *,
    doctor_id: uuid.UUID,
    appointment_at: datetime.datetime,
    exclude_appointment_id: uuid.UUID | None = None,
) -> None:
    stmt = select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_at == appointment_at,
        Appointment.status.in_(_ACTIVE_STATUSES),
    )
    if exclude_appointment_id is not None:
        stmt = stmt.where(Appointment.id != exclude_appointment_id)

    if (await db.scalars(stmt)).first() is not None:
        raise DoctorAlreadyBookedError(
            f"Doctor {doctor_id} is already booked at {appointment_at.isoformat()}"
        )


async def create_appointment(
    db: AsyncSession, data: AppointmentCreate, actor_id: uuid.UUID
) -> Appointment:
    await _ensure_patient_exists(db, data.patient_id)
    await _ensure_doctor_exists(db, data.doctor_id)

    if data.status in _ACTIVE_STATUSES:
        await _ensure_doctor_not_double_booked(
            db, doctor_id=data.doctor_id, appointment_at=data.appointment_at
        )

    appointment = Appointment(
        **data.model_dump(),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


async def get_appointment(db: AsyncSession, appointment_id: uuid.UUID) -> Appointment:
    appointment = await db.get(Appointment, appointment_id)
    if appointment is None:
        raise AppointmentNotFoundError(f"Appointment {appointment_id} not found")
    return appointment


async def list_appointments(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID | None = None,
    doctor_id: uuid.UUID | None = None,
    status: AppointmentStatus | None = None,
    appointment_type: AppointmentType | None = None,
    from_date: datetime.date | None = None,
    to_date: datetime.date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Appointment], int]:
    stmt = select(Appointment)

    if patient_id:
        stmt = stmt.where(Appointment.patient_id == patient_id)
    if doctor_id:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    if status:
        stmt = stmt.where(Appointment.status == status)
    if appointment_type:
        stmt = stmt.where(Appointment.appointment_type == appointment_type)
    if from_date:
        stmt = stmt.where(Appointment.appointment_at >= from_date)
    if to_date:
        stmt = stmt.where(Appointment.appointment_at < to_date + datetime.timedelta(days=1))

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Appointment.appointment_at.asc()).limit(limit).offset(offset)
    appointments = list((await db.scalars(stmt)).all())
    return appointments, total


async def update_appointment(
    db: AsyncSession, appointment_id: uuid.UUID, data: AppointmentUpdate, actor_id: uuid.UUID
) -> Appointment:
    appointment = await get_appointment(db, appointment_id)
    updates = data.model_dump(exclude_unset=True)

    if "patient_id" in updates:
        await _ensure_patient_exists(db, updates["patient_id"])
    if "doctor_id" in updates:
        await _ensure_doctor_exists(db, updates["doctor_id"])

    new_doctor_id = updates.get("doctor_id", appointment.doctor_id)
    new_appointment_at = updates.get("appointment_at", appointment.appointment_at)
    new_status = updates.get("status", appointment.status)

    if new_status in _ACTIVE_STATUSES:
        await _ensure_doctor_not_double_booked(
            db,
            doctor_id=new_doctor_id,
            appointment_at=new_appointment_at,
            exclude_appointment_id=appointment.id,
        )

    for field, value in updates.items():
        setattr(appointment, field, value)
    appointment.updated_by = actor_id

    await db.commit()
    await db.refresh(appointment)
    return appointment


async def delete_appointment(db: AsyncSession, appointment_id: uuid.UUID) -> None:
    appointment = await get_appointment(db, appointment_id)
    await db.delete(appointment)
    await db.commit()
