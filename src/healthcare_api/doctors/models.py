from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from healthcare_api.db.base_class import Base
from healthcare_api.db.mixins import AuditMixin


class Doctor(Base, AuditMixin):
    __tablename__ = "doctors"

    doctor_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # No ORM relationships: see the note in patients/models.py.
