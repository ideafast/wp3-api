from fastapi import FastAPI

from api.docs import router as docs
from api.patients import router as patients
from api.pipeline import router as pipeline

api = FastAPI()

api.include_router(patients, prefix="/patients")
api.include_router(docs, prefix="/docs")
api.include_router(pipeline, prefix="/pipeline")


if __name__ == "__main__":
    """Run locally with adjusted settings and loaded .envs"""
    import os

    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()
    os.environ["AIRFLOW_SERVER"] = "localhost"

    uvicorn.run("api.main:api", host="0.0.0.0", port=8000, reload=True)  # noqa: S104
