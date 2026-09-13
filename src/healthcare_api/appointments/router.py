import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from healthcare_api.api.deps import ActorId, DbSession, PaginationParams
from healthcare_api.appointments import service
from healthcare_api.appointments.models import AppointmentStatus, AppointmentType
from healthcare_api.appointments.schemas import (
    AppointmentCreate,
    AppointmentList,
    AppointmentRead,
    AppointmentUpdate,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate, db: DbSession, actor_id: ActorId
) -> AppointmentRead:
    return await service.create_appointment(db, data, actor_id)


@router.get("", response_model=AppointmentList)
async def list_appointments(
    db: DbSession,
    pagination: PaginationParams,
    patient_id: Annotated[uuid.UUID | None, Query()] = None,
    doctor_id: Annotated[uuid.UUID | None, Query()] = None,
    status: Annotated[AppointmentStatus | None, Query()] = None,
    appointment_type: Annotated[AppointmentType | None, Query()] = None,
    from_date: Annotated[datetime.date | None, Query()] = None,
    to_date: Annotated[datetime.date | None, Query()] = None,
) -> AppointmentList:
    appointments, total = await service.list_appointments(
        db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        status=status,
        appointment_type=appointment_type,
        from_date=from_date,
        to_date=to_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return AppointmentList(
        items=appointments, limit=pagination.limit, offset=pagination.offset, total=total
    )


@router.get("/{appointment_id}", response_model=AppointmentRead)
async def get_appointment(appointment_id: uuid.UUID, db: DbSession) -> AppointmentRead:
    return await service.get_appointment(db, appointment_id)


@router.patch("/{appointment_id}", response_model=AppointmentRead)
async def update_appointment(
    appointment_id: uuid.UUID, data: AppointmentUpdate, db: DbSession, actor_id: ActorId
) -> AppointmentRead:
    return await service.update_appointment(db, appointment_id, data, actor_id)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(appointment_id: uuid.UUID, db: DbSession) -> None:
    await service.delete_appointment(db, appointment_id)
