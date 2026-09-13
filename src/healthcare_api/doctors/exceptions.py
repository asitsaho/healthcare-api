class DoctorNotFoundError(Exception):
    """Raised when a doctor id does not correspond to an existing doctor."""


class DuplicateDoctorNumberError(Exception):
    """Raised when a doctor_number already exists."""


class DoctorHasDependentRecordsError(Exception):
    """Raised when deleting a doctor that still has appointments or
    medical records referencing it."""
