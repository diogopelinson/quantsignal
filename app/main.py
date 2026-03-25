import os
from contextlib import asynccontextmanager

import mlflow
import mlflow.lightgbm
from fastapi import FastAPI

from app.routers import explain, model_info, signals


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.MlflowClient()
    versions = client.get_latest_versions("quantsignal-ranker")
    run_id = versions[0].run_id

    app.state.model = mlflow.lightgbm.load_model(f"runs:/{run_id}/model")
    yield

app = FastAPI(title="QuantSignal", version="0.1.0", lifespan=lifespan)

app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(explain.router, prefix="/explain", tags=["explain"])
app.include_router(model_info.router, prefix="/model", tags=["model"])

@app.get("/health")
def health():
    return {"status": "ok"}