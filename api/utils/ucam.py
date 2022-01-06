from __future__ import annotations

import os
from datetime import datetime
from enum import IntEnum
from typing import List, Optional

import requests
from pydantic.dataclasses import dataclass


class DiseaseType(IntEnum):
    """Enum for disease types"""

    Healthy = 1  #
    HD = 2  # Huntington's
    IBD = 3  # Inflammatory bowel
    PD = 4  # Parkinson's
    PSS = 5  # Progressive systemic sclerosis
    RA = 6  # Rheumatoid arthritis
    SLE = 7  # Systemic lupus erythematosus


@dataclass
class DeviceBase:
    """Basis for device parsing"""

    # GET /devices will never return None for device_id
    # GET /patients includes VTT, thus device_id _can_ be None
    device_id: Optional[str]


@dataclass
class PatientBase:
    """Basis for patient parsing"""

    patient_id: str
    disease: DiseaseType


@dataclass
class CommonBase:
    """Basis for all parsing"""

    start_wear: datetime
    end_wear: Optional[datetime]
    deviations: Optional[str]
    vttsma_id: Optional[str]


@dataclass
class Patient(PatientBase, CommonBase):
    """Body for parsing patients"""

    # NOTE: is identical to VTT payload
    @classmethod
    def serialize(cls, payload: dict) -> Patient:
        """Serialise UCAM payloads to dataclasses"""
        return cls(
            start_wear=format_weartime(payload["start_Date"]),
            end_wear=format_weartime(payload["end_Date"])
            if payload["end_Date"]
            else None,
            deviations=payload["deviations"],
            vttsma_id=payload["vtT_id"],
            patient_id=payload["subject_id"],
            disease=DiseaseType(int(payload["subject_Group"])),
        )


@dataclass
class Device(DeviceBase, CommonBase):
    """Body for parsing Devices"""

    @classmethod
    def serialize(cls, payload: dict) -> Device:
        """Serialise UCAM payloads to dataclasses"""
        return cls(
            start_wear=format_weartime(payload["start_Date"]),
            end_wear=format_weartime(payload["end_Date"])
            if payload["end_Date"]
            else None,
            deviations=payload["deviations"],
            vttsma_id=payload["vtT_id"],
            device_id=payload["device_id"],
        )


@dataclass
class DeviceWithPatients(DeviceBase):
    """Top level body for parsing devices"""

    patients: List[Patient]

    @classmethod
    def serialize(cls, payload: dict) -> DeviceWithPatients:
        """Serialise UCAM payloads to dataclasses"""
        return cls(
            device_id=payload["device_id"],
            patients=[Patient.serialize(patients) for patients in payload["patients"]],
        )


@dataclass
class PatientWithDevices(PatientBase):
    """Top level body for parsing patients"""

    devices: List[Device]

    @classmethod
    def serialize(cls, payload: dict) -> PatientWithDevices:
        """Serialise UCAM payloads to dataclasses"""
        return cls(
            patient_id=payload["subject_id"],
            disease=DiseaseType(int(payload["subject_Group"])),
            devices=[Device.serialize(devices) for devices in payload["devices"]],
        )


def format_weartime(time: str) -> datetime:
    """create a datetime object from a UCAM provide weartime string"""
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")


def ucam_access_token() -> str:
    """Obtain (or refresh) an access token."""
    now = int(datetime.utcnow().timestamp())
    last_created = int(os.getenv("UCAM_ACCESS_TOKEN_GEN_TIME", 0))
    # Refresh the token every 1 day, i.e., below 7 day limit.
    token_expired = (last_created + (60 * 60 * 24)) <= now

    if token_expired:
        request = {
            "Username": os.getenv("UCAM_USERNAME"),
            "Password": os.getenv("UCAM_PASSWORD"),
        }

        response = requests.post(f"{os.getenv('UCAM_URI')}/user/login", json=request)
        response.raise_for_status()
        result: dict = response.json()
        access_token = result["token"]

        os.environ["UCAM_ACCESS_TOKEN"] = access_token
        os.environ["UCAM_ACCESS_TOKEN_GEN_TIME"] = str(now)

    return os.getenv("UCAM_ACCESS_TOKEN")


def response(request_url: str) -> Optional[dict]:
    """
    Perform GET request on the UCAM API
    NOTE: requests automatically converts null to None
    """
    headers = {"Authorization": f"Bearer {ucam_access_token()}"}
    url = f"{os.getenv('UCAM_URI')}{request_url}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # possibly no result
    if response.status_code == 204:
        return None

    result: dict = response.json()
    return result


def get_patients() -> Optional[List[PatientWithDevices]]:
    """Get all patients known to UCAM"""
    # NOTE: patients/patient_id returns a 204 if not found, other endpoints []
    payload = response("/patients/")
    return (
        [PatientWithDevices.serialize(patient) for patient in payload]
        if payload
        else None
    )


def get_one_patient(patient_id: str) -> Optional[PatientWithDevices]:
    """Get one patient based on the ID"""
    # NOTE: patients/patient_id returns a 204 if not found, other endpoints []
    payload = response(f"/patients/{patient_id}")
    return PatientWithDevices.serialize(payload) if payload else None


def get_devices(device_id: str = "") -> Optional[List[DeviceWithPatients]]:
    """Get one device based on the ID"""
    # always returns a list, even for one device_id
    payload = response(f"/devices/{device_id}")
    return (
        [DeviceWithPatients.serialize(device) for device in payload]
        if payload
        else None
    )
