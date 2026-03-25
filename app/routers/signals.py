from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from mlflow.tracking import MlflowClient

from app.schemas import SignalsResponse, StockSignal
from pipeline.features import build_features
from pipeline.ingest import fetch_market_data

router = APIRouter()

@router.get("", response_model=SignalsResponse)
def get_signals(
    request: Request,
    market: str = Query(default="US", enum=["US", "BR", "UK", "JP"]),
    top_n: int = Query(default=20, ge=5, le=100),
):
    try:
        model = request.app.state.model
        raw = fetch_market_data(market=market, period='2y')
        features = build_features(raw)
        scores = model.predict(features.values)
        tickers = features.index.tolist()
        ranked = sorted(zip(tickers, scores), key=lambda x: x[1], reverse=True)[:top_n]

        signals = [
            StockSignal(ticker=t, score=round(float(s), 4), rank=i + 1, market=market)
            for i, (t, s) in enumerate(ranked)
        ]
        client = MlflowClient()
        versions = client.get_latest_versions("quantsignal-ranker")
        run = client.get_run(versions[0].run_id)
        last_trained = datetime.fromtimestamp(run.info.start_time / 1000).strftime("%Y-%m-%d %H:%M")

        return SignalsResponse(
            signals=signals,
            model_version=versions[0].version,
            market=market,
            top_n=top_n,
            last_trained=last_trained
        )    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))