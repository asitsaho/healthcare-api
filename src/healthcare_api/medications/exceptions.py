class MedicationNotFoundError(Exception):
    """Raised when a medication id does not correspond to an existing medication."""


class MedicationPatientNotFoundError(Exception):
    """Raised when the referenced patient does not exist."""


class MedicationRecordNotFoundError(Exception):
    """Raised when the referenced medical record does not exist."""


class MedicationRecordPatientMismatchError(Exception):
    """Raised when the referenced medical record does not belong to the
    referenced patient."""
