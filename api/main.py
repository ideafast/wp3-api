from fastapi import FastAPI

from api.ucam import router as ucam

api = FastAPI()

api.include_router(ucam, prefix="/ucam")
