from typing import Optional

from fastapi import APIRouter

router = APIRouter()


@router.get("/patients/list")
def patients(cohort: Optional[str] = None) -> str:
    """Get a list of known patients from the UCAM DB"""
    return f"list of patients for cohort: {cohort}"
