import subprocess
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


def retrieve_latest_docs() -> None:
    """Run shell script to clone repo"""
    subprocess.call("api/utils/pull_repo.sh")


@router.post("/")
def docs() -> str:
    """Get information about all device documentation"""
    return "got your some info about all devices"


@router.get("/{device}")
def device(device: DEVICE) -> str:
    """Get information about the device documentation"""
    return f"got your some info about {device}"


@router.get("/{device}/faq")
def faq(device: DEVICE) -> str:
    """Get list of FAQ from device documentation"""
    return f"got your some FAQs about {device}"
