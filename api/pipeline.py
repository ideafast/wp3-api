from datetime import datetime
from enum import Enum
from os import getenv
from typing import Dict, List

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

HOST = f"http://{getenv('AIRFLOW_SERVER')}:8080/api/v1"
AUTH = ("localhost", getenv("WP3API_AIRFLOW_PASS"))


class PipelineHealth(Enum):
    """Traffic light health indicator"""

    RED = "red"  # The pipeline failed to run
    ORANGE = "orange"  # A task within the run failed
    GREEN = "green"  # Pipeline and tasks ran successfully


class PipelineStatus(BaseModel):
    """Pipeline device status parser"""

    last_completed: datetime
    health: PipelineHealth


# possible (expected) responses of the API - will be shown in api docs
responses = {
    200: {
        "description": "Overview of pipeline runs per device. Pipeline health"
        + f"can be any of: {[k.name for k in PipelineHealth]}",
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


@router.get("/", responses=responses)
def get_dag_run_status() -> dict:
    """Get status information about the very latest individual pipeline runs"""
    dag_ids = get_dag_run_list()

    # just focusing on the latest run
    latest_runs = {id: get_dag_dagruns(id, limit=1)[0] for id in dag_ids}

    for dag_id, run in latest_runs.items():
        tasks_status = get_dagrun_tasks(dag_id, run["dag_run_id"])
        latest_runs[dag_id]["tasks"] = tasks_status

        # determine pipeline health
        latest_runs[dag_id]["health"] = (
            PipelineHealth.RED
            if "failed" in run["state"]
            else PipelineHealth.ORANGE
            if any(["failed" in t["state"] for t in tasks_status])
            else PipelineHealth.GREEN
        )

    return {
        id: PipelineStatus(last_completed=s["start_date"], health=s["health"])
        for id, s in latest_runs.items()
    }


@router.get("/list")
def get_dag_run_list() -> list:
    """Get the list of pipelines 'names' on the server"""
    return [d["dag_id"] for d in get_airflow("/dags")["dags"]]


@router.get("/history")
def get_dag_run_status_historically() -> dict:
    """Get the history of all pipeline runs"""
    dag_ids = get_dag_run_list()

    # just focusing on the latest run
    all_runs = {id: get_all_dag_dagruns(id) for id in dag_ids}

    for dag_id, runs in all_runs.items():
        for index, run in enumerate(runs):
            tasks_status = get_dagrun_tasks(dag_id, run["dag_run_id"])
            all_runs[dag_id][index]["tasks"] = tasks_status

            # determine pipeline health
            all_runs[dag_id][index]["health"] = (
                PipelineHealth.RED
                if "failed" in run["state"]
                else PipelineHealth.ORANGE
                if any(["failed" in t["state"] for t in tasks_status])
                else PipelineHealth.GREEN
            )

    return all_runs


def get_dag_dagruns(dag_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    """Get dagruns from a particular dag_id"""
    info_of_interest = ("start_date", "dag_run_id", "state")

    payload = get_airflow(
        f"/dags/{dag_id}/dagRuns?order_by=-start_date&limit={limit}&offset={offset}"
    )["dag_runs"]

    return [{k: data[k] for k in info_of_interest} for data in payload]


def get_all_dag_dagruns(dag_id: str) -> List:
    """Get all possible dagruns from a particular dag_id"""
    runs = []
    offset, steps = 0, 100

    while past_runs := get_dag_dagruns(dag_id, limit=steps, offset=offset):
        runs.extend(past_runs)
        offset += steps

    return runs


def get_dagrun_tasks(dag_id: str, dag_run_id: str) -> List[dict]:
    """Get status information about individual pipeline run's tasks"""
    info_of_interest = ("task_id", "state")

    payload = get_airflow(f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances")[
        "task_instances"
    ]

    return [{k: task[k] for k in info_of_interest} for task in payload]
