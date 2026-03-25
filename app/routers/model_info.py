from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from mlflow.tracking import MlflowClient

from app.schemas import ModelInfoResponse

router = APIRouter()

@router.get("/info", response_model=ModelInfoResponse)
def get_model_info(request: Request):
    try:
        client = MlflowClient()
        versions = client.get_latest_versions("quantsignal-ranker")

        if not versions:
            raise HTTPException(status_code=404, detail="No model versions found")

        v = versions[0]
        run = client.get_run(v.run_id)
        last_trained = datetime.fromtimestamp(
            run.info.start_time / 1000
        ).strftime("%Y-%m-%d %H:%M")

        return ModelInfoResponse(
            model_name=v.name,
            version=v.version,
            stage=v.current_stage,
            last_trained=last_trained,
            metrics=run.data.metrics,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))