from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import signals
import os
import mlflow
import mlflow.lightgbm
from mlflow.tracking import MlflowClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    app.state.model = mlflow.lightgbm.load_model("models:/quantsignal-ranker/latest")
    yield

app = FastAPI(title="QuantSignal", version="0.1.0", lifespan=lifespan)
app.include_router(signals.router, prefix="/signals", tags=["signals"])

@app.get("/health")
def health():
    return {"status": "ok"}