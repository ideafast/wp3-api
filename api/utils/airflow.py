from datetime import datetime
from enum import Enum
from os import getenv
from typing import List, Optional

import requests
from fastapi import HTTPException
from pydantic import BaseModel, Field

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

    start_date: Optional[datetime]
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


def get_dag_dagruns(dag_id: str, limit: int = 25, offset: int = 0) -> List[PipelineRun]:
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
