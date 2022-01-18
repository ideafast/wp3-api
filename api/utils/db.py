from pydantic.dataclasses import dataclass
from typing import List, Optional
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# setup mongodb connection
myclient = MongoClient(
    host=["localhost:27017"],
    username=os.getenv('_MONGO_INITDB_ROOT_USERNAME'),
    password=os.getenv('_MONGO_INITDB_ROOT_PASSWORD')
)
mydb = myclient["credentials_db"]
mycol = mydb["crednetials_collection"]

@dataclass
class PatientsCredentials():
    """Patient credentials"""
    patient_id: str
    dreem_email: str
    dreem_password: str
    wildkeys_email: str
    wildkeys_password: str
    tfa_email: str
    tfa_password: str

def get_patients_credentials(the_id: str) -> Optional[PatientsCredentials]:
    """Get credentials for one patient based on the ID"""
    # go to mongo with patient ID
    # example K-S4YJHD
    myquery = { "patient_id": the_id }
    payload = mycol.find(myquery)
    newPay = None
    for x in payload:
        newPay = x
    print("here comes the payload")
    print(newPay)
    if newPay is not None:
        patient_credentials = PatientsCredentials(
                patient_id = the_id,
                dreem_email = newPay['dreem_email'],
                dreem_password = newPay['dreem_password'],
                wildkeys_email = newPay['wildkeys_email'],
                wildkeys_password = newPay['wildkeys_password'],
                tfa_email = newPay['tfa_email'],
                tfa_password = newPay['tfa_password']
        )
        return patient_credentials
    else:
        return None
    