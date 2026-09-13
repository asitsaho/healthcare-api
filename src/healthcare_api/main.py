"""Application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from healthcare_api.api.health import router as health_router
from healthcare_api.api.router import api_router
from healthcare_api.appointments.exceptions import (
    AppointmentDoctorNotFoundError,
    AppointmentNotFoundError,
    AppointmentPatientNotFoundError,
    DoctorAlreadyBookedError,
    InvalidAppointmentTimeError,
)
from healthcare_api.core.config import get_settings
from healthcare_api.core.logging import configure_logging
from healthcare_api.db.session import engine
from healthcare_api.doctors.exceptions import (
    DoctorHasDependentRecordsError,
    DoctorNotFoundError,
    DuplicateDoctorNumberError,
)
from healthcare_api.medical_records.exceptions import (
    MedicalRecordDoctorNotFoundError,
    MedicalRecordNotFoundError,
    MedicalRecordPatientNotFoundError,
)
from healthcare_api.medications.exceptions import (
    MedicationNotFoundError,
    MedicationPatientNotFoundError,
    MedicationRecordNotFoundError,
    MedicationRecordPatientMismatchError,
)
from healthcare_api.patients.exceptions import (
    DuplicatePatientNumberError,
    InvalidDateOfBirthError,
    PatientHasDependentRecordsError,
    PatientNotFoundError,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown.

    The engine is created at import time in ``db.session`` (httpx's
    ASGITransport does not run lifespan events, so tests would otherwise get a
    None engine). All this needs to do is dispose it.

    Disposing explicitly matters on Windows: without it, Proactor event-loop
    transports emit spurious ConnectionResetError from ``__del__`` at
    interpreter shutdown.
    """
    configure_logging(debug=settings.debug)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="A FastAPI service for the healthcare domain, backed by PostgreSQL.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)


def _domain_error_handler(status_code: int):
    """Build a handler that maps one domain error type to a fixed HTTP status.

    Keeps the mapping declarative below while ensuring the service layer
    itself never imports FastAPI.
    """

    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return handler


# 404 - the thing looked up by id does not exist.
app.add_exception_handler(PatientNotFoundError, _domain_error_handler(status.HTTP_404_NOT_FOUND))
app.add_exception_handler(DoctorNotFoundError, _domain_error_handler(status.HTTP_404_NOT_FOUND))
app.add_exception_handler(
    AppointmentNotFoundError, _domain_error_handler(status.HTTP_404_NOT_FOUND)
)
app.add_exception_handler(
    MedicalRecordNotFoundError, _domain_error_handler(status.HTTP_404_NOT_FOUND)
)
app.add_exception_handler(MedicationNotFoundError, _domain_error_handler(status.HTTP_404_NOT_FOUND))

# 409 - conflicts with existing data.
app.add_exception_handler(
    DuplicatePatientNumberError, _domain_error_handler(status.HTTP_409_CONFLICT)
)
app.add_exception_handler(
    DuplicateDoctorNumberError, _domain_error_handler(status.HTTP_409_CONFLICT)
)
app.add_exception_handler(DoctorAlreadyBookedError, _domain_error_handler(status.HTTP_409_CONFLICT))
app.add_exception_handler(
    PatientHasDependentRecordsError, _domain_error_handler(status.HTTP_409_CONFLICT)
)
app.add_exception_handler(
    DoctorHasDependentRecordsError, _domain_error_handler(status.HTTP_409_CONFLICT)
)

# 422 - invalid request data, or a referenced entity that does not exist.
app.add_exception_handler(
    InvalidDateOfBirthError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    InvalidAppointmentTimeError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    AppointmentPatientNotFoundError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    AppointmentDoctorNotFoundError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    MedicalRecordPatientNotFoundError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    MedicalRecordDoctorNotFoundError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    MedicationPatientNotFoundError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    MedicationRecordNotFoundError, _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
)
app.add_exception_handler(
    MedicationRecordPatientMismatchError,
    _domain_error_handler(status.HTTP_422_UNPROCESSABLE_ENTITY),
)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """The one endpoint that proves the scaffold is alive."""
    return {
        "name": settings.app_name,
        "environment": settings.environment,
        "docs": "/docs",
    }


app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)
