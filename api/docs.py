import codecs
import subprocess  # noqa
from enum import Enum
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

CURRENT_DIR = Path(__file__).parent
FILES_PATH = CURRENT_DIR / "docs/html"


class DEVICE(Enum):
    """Enum for device types"""

    DRM = "DRM"
    VTP = "VTP"
    AX6 = "AX6"
    SMP = "SMP"
    WKS = "WKS"
    CTB = "CTB"

    # we also want to host documentation about software platforms
    UCAM = "UCAM"
    DMP = "DMP"

    # referring to documentation about how to update this documentsion
    DOCS = "DOCS"


def load_doc(device: DEVICE, type: str = "docs") -> str:
    """Read the requested file into memory and return"""
    try:
        with codecs.open(f"{FILES_PATH}/{type}/{device.name}.html", "r") as f:
            content = f.read()
            return content
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="File not found") from e


def retrieve_latest_docs() -> None:
    """Run shell script to pull latest changes to the DOC/FAQ repo"""
    subprocess.run(["git", "-C", "api/docs/", "pull"])  # noqa


@router.post("/update", status_code=202, include_in_schema=False)
def update_docs(payload: dict, background_tasks: BackgroundTasks) -> dict:
    """Trigger an update for the docs from Github Actions"""
    background_tasks.add_task(retrieve_latest_docs)
    return {"message": "Success: updating cache of Docs/API is scheduled"}


@router.get("/list", response_model=List[str])
def list_devices() -> List[str]:
    """Return a list of possible devices/software to get docs for"""
    return [d.name for d in DEVICE]


@router.get("/{device}", response_class=HTMLResponse)
def device(device: DEVICE) -> str:
    """Get information about the device documentation"""
    return load_doc(device)


@router.get("/{device}/faq", response_class=HTMLResponse)
def faq(device: DEVICE) -> str:
    """Get list of FAQ from device documentation"""
    return load_doc(device, "faq")
