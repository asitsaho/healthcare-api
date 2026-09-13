class MedicalRecordNotFoundError(Exception):
    """Raised when a medical record id does not correspond to an existing record."""


class MedicalRecordPatientNotFoundError(Exception):
    """Raised when the referenced patient does not exist."""


class MedicalRecordDoctorNotFoundError(Exception):
    """Raised when the referenced doctor does not exist."""
