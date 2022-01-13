from fastapi import BackgroundTasks, FastAPI
from fastapi.staticfiles import StaticFiles

from api.patients import router as patients
from api.pipeline import router as pipeline

api = FastAPI(docs_url="/swagger", redoc_url="/redoc")

api.include_router(patients, prefix="/patients")
api.include_router(pipeline, prefix="/status")


@api.post("/update_docs", status_code=202)
def update_docs(payload: dict, background_tasks: BackgroundTasks) -> dict:
    """Trigger an update for the docs from Github Actions"""
    # background_tasks.add_task(retrieve_latest_docs)
    return {"message": "Success: updating cache of Docs/API is scheduled"}


api.mount("/docs", StaticFiles(directory="docs/html"))
