import datetime
import enum

from sqlalchemy import CheckConstraint, Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from healthcare_api.db.base_class import Base
from healthcare_api.db.mixins import AuditMixin


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class Patient(Base, AuditMixin):
    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint(
            "date_of_birth <= CURRENT_DATE",
            name="ck_patients_date_of_birth_not_future",
        ),
    )

    patient_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    gender: Mapped[Gender] = mapped_column(
        Enum(
            Gender,
            name="gender",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # No ORM relationships: dependent-record checks and joins are done with
    # explicit queries in the service layer (see appointments/medical_records
    # service modules), which keeps this model safe to use with an
    # AsyncSession without risking an implicit lazy-load.
