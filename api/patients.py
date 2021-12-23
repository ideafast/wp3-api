from enum import Enum
from typing import List, Optional

from fastapi import APIRouter

router = APIRouter()


class ORDER(Enum):
    """Enum for order_by options"""

    UID = "uid"
    LOCALID = "localid"
    DISEASE = "disease"


class DiseaseType(Enum):
    """Enum for disease types"""

    Healthy = 1  #
    HD = 2  # Huntington's
    IBD = 3  # Inflammatory bowel
    PD = 4  # Parkinson's
    PSS = 5  # Progressive systemic sclerosis
    RA = 6  # Rheumatoid arthritis
    SLE = 7  # Systemic lupus erythematosus


@router.get("/")
def patients(
    cohort: Optional[str] = None, orderby: Optional[ORDER] = None
) -> List[Optional[str]]:
    """Get a list of known patients"""
    if cohort:
        return ["A-PATIENT", "B-PATIENT", "C-PATIENT"]
    if orderby:
        return [f"ordering by {orderby}"]

    return []


@router.get("/{id}")
def details(id: str) -> str:
    """Get more details about a patient"""
    return f"more details for patient: {id}"


@router.get("/{id}/auth")
def auth(id: str) -> str:
    """Get authentication details for a patient"""
    return f"pass and login for patient: {id}"
