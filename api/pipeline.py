from os import getenv

import requests
from fastapi import APIRouter

router = APIRouter()

HOST = f"http://{getenv('AIRFLOW_SERVER')}:8080/api/v1"
AUTH = ("localhost", getenv("WP3API_AIRFLOW_PASS"))


def get_airflow(endpoint: str) -> dict:
    """Wrap requests for generalised Airflow GET requests"""
    response = requests.get(HOST + endpoint, auth=AUTH)
    response.raise_for_status()
    result: dict = response.json()
    return result


@router.get("/")
def status() -> dict:
    """Get status information about the ETL pipeline"""
    dag_ids = [d["dag_id"] for d in get_airflow("/dags")["dags"]]
    past_dag_run_status = {
        id: _parse_status(
            get_airflow(f"/dags/{id}/dagRuns?limit=50&order_by=-start_date")["dag_runs"]
        )
        for id in dag_ids
    }
    # TODO: add scheduled runs status (inc. if retries are set)

    return past_dag_run_status


def _parse_status(dag_runs: dict) -> dict:
    """Parse the Airflow API payload for readability"""
    last_ok = next(
        (index for (index, d) in enumerate(dag_runs) if d["state"] == "success"), None
    )
    # search for 'failed' status, but no further than the latest succes
    last_bad = next(
        (
            index
            for (index, d) in enumerate(dag_runs[:last_ok])
            if d["state"] == "failed"
        ),
        0,
    )

    return {
        "last_completed": (
            dag_runs[last_ok]["start_date"] if last_ok is not None else None
        ),
        "failed_runs_since": (last_bad if last_ok is not None else len(dag_runs)),
    }
