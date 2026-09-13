import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from healthcare_api.api.deps import ActorId, DbSession, PaginationParams
from healthcare_api.medical_records import service
from healthcare_api.medical_records.models import RecordType
from healthcare_api.medical_records.schemas import (
    MedicalRecordCreate,
    MedicalRecordList,
    MedicalRecordRead,
    MedicalRecordUpdate,
)

router = APIRouter(prefix="/medical-records", tags=["medical-records"])

# Mounted separately under /patients/{patient_id}/medical-records.
patient_records_router = APIRouter(tags=["medical-records"])


@router.post("", response_model=MedicalRecordRead, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    data: MedicalRecordCreate, db: DbSession, actor_id: ActorId
) -> MedicalRecordRead:
    return await service.create_medical_record(db, data, actor_id)


@router.get("", response_model=MedicalRecordList)
async def list_medical_records(
    db: DbSession,
    pagination: PaginationParams,
    patient_id: Annotated[uuid.UUID | None, Query()] = None,
    doctor_id: Annotated[uuid.UUID | None, Query()] = None,
    record_type: Annotated[RecordType | None, Query()] = None,
    from_date: Annotated[datetime.date | None, Query()] = None,
    to_date: Annotated[datetime.date | None, Query()] = None,
) -> MedicalRecordList:
    records, total = await service.list_medical_records(
        db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        record_type=record_type,
        from_date=from_date,
        to_date=to_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return MedicalRecordList(
        items=records, limit=pagination.limit, offset=pagination.offset, total=total
    )


@router.get("/{record_id}", response_model=MedicalRecordRead)
async def get_medical_record(record_id: uuid.UUID, db: DbSession) -> MedicalRecordRead:
    return await service.get_medical_record(db, record_id)


@router.patch("/{record_id}", response_model=MedicalRecordRead)
async def update_medical_record(
    record_id: uuid.UUID, data: MedicalRecordUpdate, db: DbSession, actor_id: ActorId
) -> MedicalRecordRead:
    return await service.update_medical_record(db, record_id, data, actor_id)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_record(record_id: uuid.UUID, db: DbSession) -> None:
    await service.delete_medical_record(db, record_id)


@patient_records_router.get(
    "/patients/{patient_id}/medical-records", response_model=MedicalRecordList
)
async def list_records_for_patient(
    patient_id: uuid.UUID, db: DbSession, pagination: PaginationParams
) -> MedicalRecordList:
    records, total = await service.list_medical_records(
        db, patient_id=patient_id, limit=pagination.limit, offset=pagination.offset
    )
    return MedicalRecordList(
        items=records, limit=pagination.limit, offset=pagination.offset, total=total
    )
