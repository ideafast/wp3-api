from fastapi import FastAPI

from api.docs import router as docs
from api.patients import router as patients

api = FastAPI()

api.include_router(patients, prefix="/patients")
api.include_router(docs, prefix="/docs")
