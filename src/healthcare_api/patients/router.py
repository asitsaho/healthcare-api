import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from healthcare_api.api.deps import ActorId, DbSession, PaginationParams
from healthcare_api.patients import service
from healthcare_api.patients.models import Gender
from healthcare_api.patients.schemas import PatientCreate, PatientList, PatientRead, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(data: PatientCreate, db: DbSession, actor_id: ActorId) -> PatientRead:
    return await service.create_patient(db, data, actor_id)


@router.get("", response_model=PatientList)
async def list_patients(
    db: DbSession,
    pagination: PaginationParams,
    name: Annotated[str | None, Query()] = None,
    patient_number: Annotated[str | None, Query()] = None,
    gender: Annotated[Gender | None, Query()] = None,
) -> PatientList:
    patients, total = await service.list_patients(
        db,
        name=name,
        patient_number=patient_number,
        gender=gender,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return PatientList(
        items=patients, limit=pagination.limit, offset=pagination.offset, total=total
    )


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(patient_id: uuid.UUID, db: DbSession) -> PatientRead:
    return await service.get_patient(db, patient_id)


@router.patch("/{patient_id}", response_model=PatientRead)
async def update_patient(
    patient_id: uuid.UUID, data: PatientUpdate, db: DbSession, actor_id: ActorId
) -> PatientRead:
    return await service.update_patient(db, patient_id, data, actor_id)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: uuid.UUID, db: DbSession) -> None:
    await service.delete_patient(db, patient_id)
