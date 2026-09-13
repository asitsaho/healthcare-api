class PatientNotFoundError(Exception):
    """Raised when a patient id does not correspond to an existing patient."""


class DuplicatePatientNumberError(Exception):
    """Raised when a patient_number already exists."""


class InvalidDateOfBirthError(Exception):
    """Raised when date_of_birth is in the future."""


class PatientHasDependentRecordsError(Exception):
    """Raised when deleting a patient that still has appointments or
    medical records referencing it."""
