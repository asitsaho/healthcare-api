import datetime
import enum
import uuid

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from healthcare_api.db.base_class import Base
from healthcare_api.db.mixins import AuditMixin


class MedicationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"


class Medication(Base, AuditMixin):
    __tablename__ = "medications"
    __table_args__ = (
        Index("ix_medications_patient_id", "patient_id"),
        Index("ix_medications_medical_record_id", "medical_record_id"),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    medical_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    status: Mapped[MedicationStatus] = mapped_column(
        Enum(
            MedicationStatus,
            name="medication_status",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=MedicationStatus.ACTIVE,
    )

    # No ORM relationships: see the note in patients/models.py.
