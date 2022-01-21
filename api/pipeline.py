from typing import Dict, List

from fastapi import APIRouter

from api.utils.airflow import (
    PipelineRun,
    PipelineStatus,
    get_airflow,
    get_all_dag_dagruns,
    get_dag_dagruns,
    update_run_health,
)

router = APIRouter()


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
