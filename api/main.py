from fastapi import FastAPI

from api.docs import router as docs
from api.patients import router as patients
from api.pipeline import router as pipeline

api = FastAPI(docs_url="/swagger", redoc_url="/redoc")

api.include_router(patients, prefix="/patients")
api.include_router(docs, prefix="/docs")
api.include_router(pipeline, prefix="/status")
