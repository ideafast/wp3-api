from datetime import datetime
from enum import Enum
from os import getenv
from typing import Dict, List

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

HOST = f"http://{getenv('AIRFLOW_SERVER')}:8080/api/v1"
AUTH = ("localhost", getenv("WP3API_AIRFLOW_PASS"))


class PipelineHealth(Enum):
    """Traffic light health indicator"""

    RED = "red"  # The pipeline failed to run
    ORANGE = "orange"  # A task within the run failed
    GREEN = "green"  # Pipeline and tasks ran successfully
    UNKNOWN = "unknown"  # Cannot determine health


class PipelineStatus(BaseModel):
    """Pipeline device status parser"""

    last_completed: datetime
    health: PipelineHealth


class PipelineTask(BaseModel):
    """Task parser"""

    task_id: str
    state: str


class PipelineRun(BaseModel):
    """Pipeline run status model"""

    start_date: datetime
    dag_run_id: str
    state: str
    health: PipelineHealth = PipelineHealth.UNKNOWN
    tasks: List[PipelineTask] = Field(default_factory=list)


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


@router.get("/", response_model=Dict[str, PipelineStatus])
def get_dag_run_status() -> dict:
    """Get status information about the very latest individual pipeline runs"""
    dag_ids = get_dag_run_list()

    # just focusing on the latest run
    latest_runs = {id: get_dag_dagruns(id)[0] for id in dag_ids}

    for dag_id, run in latest_runs.items():
        update_run_health(dag_id, run)

    return {
        id: PipelineStatus(last_completed=run.start_date, health=run.health)
        for id, run in latest_runs.items()
    }


@router.get("/list", response_model=List[str])
def get_dag_run_list() -> List[str]:
    """Get the list of pipelines 'names' on the server"""
    return [d["dag_id"] for d in get_airflow("/dags")["dags"]]


@router.get("/history", response_model=Dict[str, List[PipelineRun]])
def get_dag_run_status_historically() -> dict:
    """Get the history of all pipeline runs"""
    dag_ids = get_dag_run_list()

    # just focusing on the latest run
    all_runs = {id: get_all_dag_dagruns(id) for id in dag_ids}

    # evaluate all runs. NOTE: changes mutable iterable whilst iterating
    for dag_id, runs in all_runs.items():
        for run in runs:
            update_run_health(dag_id, run)

    return all_runs


def get_dag_dagruns(dag_id: str, limit: int = 1, offset: int = 0) -> List[PipelineRun]:
    """Get dagruns from a particular dag_id"""
    payload = get_airflow(
        f"/dags/{dag_id}/dagRuns?order_by=-start_date&limit={limit}&offset={offset}"
    )["dag_runs"]
    return [PipelineRun(**p) for p in payload]


def get_all_dag_dagruns(dag_id: str) -> List[PipelineRun]:
    """Get all possible dagruns from a particular dag_id"""
    runs, offset, steps = [], 0, 100

    while past_runs := get_dag_dagruns(dag_id, limit=steps, offset=offset):
        runs.extend(past_runs)
        offset += steps

    return runs


def get_dagrun_tasks(dag_id: str, dag_run_id: str) -> List[PipelineTask]:
    """Get status information about individual pipeline run's tasks"""
    payload = get_airflow(f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances")[
        "task_instances"
    ]
    return [PipelineTask(**p) for p in payload]


def update_run_health(dag_id: str, run: PipelineRun) -> None:
    """Get tasks and determine health of the run"""
    # NOTE: Modifies the mutable PipelineRun in place

    run.tasks = get_dagrun_tasks(dag_id, run.dag_run_id)
    # determine pipeline health
    run.health = (
        PipelineHealth.RED
        if "failed" in run.state
        else PipelineHealth.ORANGE
        if any(["failed" in t.state for t in run.tasks])
        else PipelineHealth.GREEN
    )
