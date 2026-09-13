import datetime
import enum
import uuid

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from healthcare_api.db.base_class import Base
from healthcare_api.db.mixins import AuditMixin


class RecordType(str, enum.Enum):
    DIAGNOSIS = "diagnosis"
    LAB_RESULT = "lab_result"
    PROCEDURE = "procedure"
    CLINICAL_NOTE = "clinical_note"


class MedicalRecord(Base, AuditMixin):
    __tablename__ = "medical_records"
    __table_args__ = (
        Index("ix_medical_records_patient_id", "patient_id"),
        Index("ix_medical_records_record_date", "record_date"),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("doctors.id"), nullable=False
    )
    record_type: Mapped[RecordType] = mapped_column(
        Enum(
            RecordType,
            name="record_type",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    diagnosis: Mapped[str | None] = mapped_column(String(500), nullable=True)
    treatment: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    record_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # No ORM relationships: see the note in patients/models.py. Medications
    # have no independent lifecycle - they are removed together with the
    # medical record that prescribed them via the database-level
    # `ON DELETE CASCADE` on medications.medical_record_id, not an ORM
    # cascade (which would need the collection loaded first).
