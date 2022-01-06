from datetime import datetime
from os import getenv
from typing import Dict

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

HOST = f"http://{getenv('AIRFLOW_SERVER')}:8080/api/v1"
AUTH = ("localhost", getenv("WP3API_AIRFLOW_PASS"))


class PipelineStatus(BaseModel):
    """Pipeline device status parser"""

    last_completed: datetime
    failed_runs_since: int


# possible (expected) responses of the API - will be shown in api docs
responses = {
    200: {
        "description": "Overview of pipeline runs per device",
        "model": Dict[str, PipelineStatus],
    },
    502: {"description": "Internal connection error with IDEAFAST ETL Pipeline"},
}


def get_airflow(endpoint: str) -> dict:
    """Wrap requests for generalised Airflow GET requests"""
    try:
        response = requests.get(HOST + endpoint, auth=AUTH)
    except requests.exceptions.ConnectionError as e:
        # Airflow server most likely not accessible
        raise HTTPException(
            status_code=502, detail="Error with Apache Airflow Connection"
        ) from e

    response.raise_for_status()
    result: dict = response.json()
    return result


def _parse_status(dag_runs: dict) -> dict:
    """Parse the Airflow API payload for readability"""
    last_ok = next(
        (index for (index, d) in enumerate(dag_runs) if d["state"] == "success"), None
    )

    # count for 'failed' status up to latest success
    count_bad = len([1 for d in dag_runs[:last_ok] if d["state"] == "failed"])

    return PipelineStatus(
        last_completed=dag_runs[last_ok]["start_date"] if last_ok is not None else None,
        failed_runs_since=count_bad,
    )


@router.get("/", responses=responses)
def status() -> dict:
    """Get status information about the ETL pipeline"""
    dag_ids = [d["dag_id"] for d in get_airflow("/dags")["dags"]]

    result = {
        id: _parse_status(
            get_airflow(f"/dags/{id}/dagRuns?limit=50&order_by=-start_date")["dag_runs"]
        )
        for id in dag_ids
    }
    # TODO: add scheduled runs status (inc. if retries are set)

    return result
