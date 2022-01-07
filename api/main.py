from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from api.docs import router as docs
from api.patients import router as patients
from api.pipeline import router as pipeline

api = FastAPI(docs_url="/swagger", redoc_url="/redoc")

api.include_router(patients, prefix="/patients")
api.include_router(docs, prefix="/docs")
api.include_router(pipeline, prefix="/status")


@api.on_event("startup")
@repeat_every(seconds=86400)
def get_latest_docs() -> None:
    """Clone the documentation repo on a daily basis to serve over API"""
    print("cloning FAQ and DOC repository")
