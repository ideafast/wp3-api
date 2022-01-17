import operator
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Query

from api.utils.ucam import PatientWithDevices, get_one_patient, get_patients
from api.utils.db import get_patients_credentials, PatientsCredentials

router = APIRouter()


class ORDER(Enum):
    """Enum for order_by options"""

    UID = "uid"
    LOCALID = "localid"
    DISEASE = "disease"
    ID = "patient_id"


@router.get("/", response_model=List[PatientWithDevices])
def patients(
    cohort: Optional[str] = Query(None, max_length=1, regex="[A-Z]"),  # noqa: B008
    orderby: Optional[ORDER] = None,
) -> Optional[List[PatientWithDevices]]:
    """Get a list of known patients"""
    patients = get_patients()

    if cohort:
        patients = [p for p in patients if p.patient_id[0] == cohort]

    if orderby:
        patients = sorted(patients, key=operator.attrgetter(orderby.value))

    return patients


@router.get("/credentials/{id}", response_model=PatientsCredentials)
def one_patients_credentials(id: str) -> Optional[PatientsCredentials]:
    """Return list of all technology platform credentials for this patient"""
    return get_patients_credentials(id)


@router.get("/{id}", response_model=PatientWithDevices)
def one_patient(id: str) -> Optional[PatientWithDevices]:
    """Get more details about a patient"""
    return get_one_patient(id)
