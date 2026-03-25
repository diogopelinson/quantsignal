import os
from contextlib import asynccontextmanager

import mlflow
import mlflow.lightgbm
from fastapi import FastAPI

from app.routers import explain, model_info, signals


@asynccontextmanager
async def lifespan(app: FastAPI):
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    app.state.model = mlflow.lightgbm.load_model("models:/quantsignal-ranker/latest")
    yield

app = FastAPI(title="QuantSignal", version="0.1.0", lifespan=lifespan)

app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(explain.router, prefix="/explain", tags=["explain"])
app.include_router(model_info.router, prefix="/model", tags=["model"])

@app.get("/health")
def health():
    return {"status": "ok"}