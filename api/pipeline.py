from os import getenv

import requests
from fastapi import APIRouter

router = APIRouter()

HOST = f"http://{getenv('AIRFLOW_SERVER')}:8080/api/v1"
AUTH = ("localhost", getenv("WP3API_AIRFLOW_PASS"))


@router.get("/")
def status() -> dict:
    """Get status information about the ETL pipeline"""
    # GET LIST OF DAGS
    response = requests.get(f"{HOST}/dags", auth=AUTH)
    response.raise_for_status()
    result: dict = response.json()
    return result
