from enum import Enum

from fastapi import APIRouter

router = APIRouter()


class DEVICE(Enum):
    """Enum for device types"""

    DRM = "dreem"
    VTP = "vitalpatch"
    AX6 = "axivity"
    SMP = "smartphone"
    WKS = "wildkeys"
    CTB = "cantab"


@router.post("/")
def docs() -> str:
    """Get information about all device documentation"""
    return "got your some info about all devices"


@router.post("/update", status_code=201)
def update_docs(payload: dict) -> bool:
    """Trigger an update for the docs from Github Actions"""
    # return the latest git commit to confirm update succeeded
    # FOR TESTING ONLY NOW
    print(payload)
    # TODO: trigger script/task that then downloads the new repo updates
    return True


@router.get("/{device}")
def device(device: DEVICE) -> str:
    """Get information about the device documentation"""
    return f"got your some info about {device}"


@router.get("/{device}/faq")
def faq(device: DEVICE) -> str:
    """Get list of FAQ from device documentation"""
    return f"got your some FAQs about {device}"
