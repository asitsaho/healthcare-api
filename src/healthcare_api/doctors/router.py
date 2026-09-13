import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from healthcare_api.api.deps import ActorId, DbSession, PaginationParams
from healthcare_api.doctors import service
from healthcare_api.doctors.schemas import DoctorCreate, DoctorList, DoctorRead, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
async def create_doctor(data: DoctorCreate, db: DbSession, actor_id: ActorId) -> DoctorRead:
    return await service.create_doctor(db, data, actor_id)


@router.get("", response_model=DoctorList)
async def list_doctors(
    db: DbSession,
    pagination: PaginationParams,
    name: Annotated[str | None, Query()] = None,
    specialization: Annotated[str | None, Query()] = None,
) -> DoctorList:
    doctors, total = await service.list_doctors(
        db,
        name=name,
        specialization=specialization,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return DoctorList(items=doctors, limit=pagination.limit, offset=pagination.offset, total=total)


@router.get("/{doctor_id}", response_model=DoctorRead)
async def get_doctor(doctor_id: uuid.UUID, db: DbSession) -> DoctorRead:
    return await service.get_doctor(db, doctor_id)


@router.patch("/{doctor_id}", response_model=DoctorRead)
async def update_doctor(
    doctor_id: uuid.UUID, data: DoctorUpdate, db: DbSession, actor_id: ActorId
) -> DoctorRead:
    return await service.update_doctor(db, doctor_id, data, actor_id)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(doctor_id: uuid.UUID, db: DbSession) -> None:
    await service.delete_doctor(db, doctor_id)
