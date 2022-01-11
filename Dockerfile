FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ssh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./scripts /app
COPY ./api /app/api