from fastapi import APIRouter

from healthcare_api.appointments.router import router as appointments_router
from healthcare_api.doctors.router import router as doctors_router
from healthcare_api.medical_records.router import patient_records_router
from healthcare_api.medical_records.router import router as medical_records_router
from healthcare_api.medications.router import patient_medications_router
from healthcare_api.medications.router import router as medications_router
from healthcare_api.patients.router import router as patients_router

api_router = APIRouter()

api_router.include_router(patients_router)
api_router.include_router(doctors_router)
api_router.include_router(appointments_router)
api_router.include_router(medical_records_router)
api_router.include_router(medications_router)

# Nested, patient-scoped read endpoints.
api_router.include_router(patient_records_router)
api_router.include_router(patient_medications_router)
