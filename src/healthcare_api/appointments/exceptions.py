class AppointmentNotFoundError(Exception):
    """Raised when an appointment id does not correspond to an existing appointment."""


class AppointmentPatientNotFoundError(Exception):
    """Raised when the referenced patient does not exist."""


class AppointmentDoctorNotFoundError(Exception):
    """Raised when the referenced doctor does not exist."""


class DoctorAlreadyBookedError(Exception):
    """Raised when the doctor already has an active appointment at the
    requested time."""


class InvalidAppointmentTimeError(Exception):
    """Raised when the requested appointment time is not valid (e.g. in the past)."""
