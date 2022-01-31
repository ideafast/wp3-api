from typing import Dict, List, Optional

from fastapi import APIRouter

from api.utils.airflow import (
    PipelineHealth,
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
    dag_list = get_dag_run_list_with_schedules()
    dag_ids = dag_list.keys()

    # only get the latest succesfull run
    latest_runs = {
        id: next((run for run in get_dag_dagruns(id) if run.state == "success"), None)
        for id in dag_ids
    }

    for dag_id, run in latest_runs.items():
        # pipeline could also _not_ have run yet..
        if run:
            update_run_health(dag_id, run)

    return {
        id: PipelineStatus(
            # if the pipeline never ran, use None/Unknown
            last_completed=run.start_date if run else None,
            health=run.health if run else PipelineHealth.UNKNOWN,
            schedule_interval=dag_list[id],
        )
        for id, run in latest_runs.items()
    }


@router.get("/list", response_model=Dict[str, Optional[str]])
def get_dag_run_list_with_schedules() -> Dict[str, Optional[str]]:
    """Get the list of pipelines and their schedules"""
    return {
        d["dag_id"]: d["schedule_interval"]["value"]
        # schedule interval is ignored if DAG is 'paused' (often manually)
        if d["schedule_interval"] is not None and not d["is_paused"] else None
        for d in get_airflow("/dags")["dags"]
    }


@router.get("/history", response_model=Dict[str, List[PipelineRun]])
def get_dag_run_status_historically() -> dict:
    """Get the history of all pipeline runs"""
    dag_ids = get_dag_run_list_with_schedules()

    # just focusing on the latest run
    all_runs = {id: get_all_dag_dagruns(id) for id in dag_ids.keys()}

    # evaluate all runs. NOTE: changes mutable iterable whilst iterating
    for dag_id, runs in all_runs.items():
        for run in runs:
            update_run_health(dag_id, run)

    return all_runs
