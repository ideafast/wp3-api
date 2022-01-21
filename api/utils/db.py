import os
from typing import Optional

from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
from pymongo import MongoClient

load_dotenv()

# setup mongodb connection
myclient = MongoClient(
    host=[f"{os.getenv('_MONGO_HOST')}:27017"],
    username=os.getenv("_MONGO_INITDB_ROOT_USERNAME"),
    password=os.getenv("_MONGO_INITDB_ROOT_PASSWORD"),
)
mydb = myclient[os.getenv("_MONGO_INITDB_DATABASE")]
mycol = mydb[os.getenv("_MONGO_INITDB_COLLECTION")]


@dataclass
class PatientsCredentials:
    """Patient credentials"""

    _id: str
    patient_id: str
    dreem_email: str
    dreem_password: str
    wildkeys_email: str
    wildkeys_password: str
    tfa_email: str
    tfa_password: str


def get_patients_credentials(the_id: str) -> Optional[PatientsCredentials]:
    """Get credentials for one patient based on the ID"""
    myquery = {"patient_id": the_id}
    payload = list(mycol.find(myquery))
    if payload:
        patient_credentials = PatientsCredentials(**payload[0])
        return patient_credentials
    else:
        return None
