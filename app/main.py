import os

from fastapi import FastAPI

APP_VERSION = os.getenv("APP_VERSION", "0.0.0")
GIT_SHA = os.getenv("GIT_SHA", "unknown")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

app = FastAPI(title="multi-env-cicd-demo")


@app.get("/")
def root():
    return {"message": "hello", "environment": ENVIRONMENT}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "environment": ENVIRONMENT,
    }
