import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from healthcare_api.api.deps import ActorId, DbSession, PaginationParams
from healthcare_api.medications import service
from healthcare_api.medications.models import MedicationStatus
from healthcare_api.medications.schemas import (
    MedicationCreate,
    MedicationList,
    MedicationRead,
    MedicationUpdate,
)

router = APIRouter(prefix="/medications", tags=["medications"])

# Mounted separately under /patients/{patient_id}/medications.
patient_medications_router = APIRouter(tags=["medications"])


@router.post("", response_model=MedicationRead, status_code=status.HTTP_201_CREATED)
async def create_medication(
    data: MedicationCreate, db: DbSession, actor_id: ActorId
) -> MedicationRead:
    return await service.create_medication(db, data, actor_id)


@router.get("", response_model=MedicationList)
async def list_medications(
    db: DbSession,
    pagination: PaginationParams,
    patient_id: Annotated[uuid.UUID | None, Query()] = None,
    medical_record_id: Annotated[uuid.UUID | None, Query()] = None,
    status: Annotated[MedicationStatus | None, Query()] = None,
) -> MedicationList:
    medications, total = await service.list_medications(
        db,
        patient_id=patient_id,
        medical_record_id=medical_record_id,
        status=status,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return MedicationList(
        items=medications, limit=pagination.limit, offset=pagination.offset, total=total
    )


@router.get("/{medication_id}", response_model=MedicationRead)
async def get_medication(medication_id: uuid.UUID, db: DbSession) -> MedicationRead:
    return await service.get_medication(db, medication_id)


@router.patch("/{medication_id}", response_model=MedicationRead)
async def update_medication(
    medication_id: uuid.UUID, data: MedicationUpdate, db: DbSession, actor_id: ActorId
) -> MedicationRead:
    return await service.update_medication(db, medication_id, data, actor_id)


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(medication_id: uuid.UUID, db: DbSession) -> None:
    await service.delete_medication(db, medication_id)


@patient_medications_router.get("/patients/{patient_id}/medications", response_model=MedicationList)
async def list_medications_for_patient(
    patient_id: uuid.UUID, db: DbSession, pagination: PaginationParams
) -> MedicationList:
    medications, total = await service.list_medications(
        db, patient_id=patient_id, limit=pagination.limit, offset=pagination.offset
    )
    return MedicationList(
        items=medications, limit=pagination.limit, offset=pagination.offset, total=total
    )
