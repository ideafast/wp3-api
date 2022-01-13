import codecs
import subprocess
from enum import Enum
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

CURRENT_DIR = Path(__file__).parent
FILES_PATH = CURRENT_DIR / "docs/html"


class DEVICE(Enum):
    """Enum for device types"""

    DRM = "dreem"
    VTP = "vitalpatch"
    AX6 = "axivity"
    SMP = "smartphone"
    WKS = "wildkeys"
    CTB = "cantab"


def load_doc(device: DEVICE, type: str = "docs") -> str:
    """Read the requested file into memory and return"""
    try:
        with codecs.open(f"{FILES_PATH}/{type}/{device.name}.html", "r") as f:
            content = f.read()
            return content
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="File not found") from e


def retrieve_latest_docs() -> None:
    """Run shell script to clone repo"""
    subprocess.run(["git", "--git-dir", "api/docs/.git", "pull"])


@router.post("/update", status_code=202)
def update_docs(payload: dict, background_tasks: BackgroundTasks) -> dict:
    """Trigger an update for the docs from Github Actions"""
    # background_tasks.add_task(retrieve_latest_docs)
    return {"message": "Success: updating cache of Docs/API is scheduled"}


@router.get("/{device}", response_class=HTMLResponse)
def device(device: DEVICE) -> str:
    """Get information about the device documentation"""
    return load_doc(device)


@router.get("/{device}/faq", response_class=HTMLResponse)
def faq(device: DEVICE) -> str:
    """Get list of FAQ from device documentation"""
    return load_doc(device, "faq")
