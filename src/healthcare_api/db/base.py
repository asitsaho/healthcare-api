# Import every ORM model here so that:
#   1. `Base.metadata` knows about the full schema.
#   2. Alembic's `--autogenerate` can diff the real schema against the models.
#
# This module has no other purpose - never import it from application code,
# only from `alembic/env.py`.

from healthcare_api.appointments.models import Appointment  # noqa: F401
from healthcare_api.db.base_class import Base  # noqa: F401
from healthcare_api.doctors.models import Doctor  # noqa: F401
from healthcare_api.medical_records.models import MedicalRecord  # noqa: F401
from healthcare_api.medications.models import Medication  # noqa: F401
from healthcare_api.patients.models import Patient  # noqa: F401
